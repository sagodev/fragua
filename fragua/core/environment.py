"""Fragua execution environment.

Defines the orchestration layer for executing ETL functions
using a single agent, a registry and a runtime warehouse.
"""

from typing import Any, Callable, Dict, Iterable, List

from fragua.builders.pipeline_builder import FraguaPipelineBuilder
from fragua.core.agent import FraguaAgent
from fragua.core.box import FraguaBox
from fragua.core.pipeline import FraguaPipeline
from fragua.core.registry import FraguaRegistry
from fragua.core.step import FraguaStep
from fragua.builders.step_builder import FraguaStepBuilder
from fragua.core.step_index import FraguaStepIndex
from fragua.core.warehouse import FraguaWarehouse
from fragua.core.set import FraguaSet


class FraguaEnvironment:
    """
    Execution environment for Fragua.

    An environment owns exactly one agent, one registry
    and one runtime warehouse.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.agent = FraguaAgent(name=f"{name}_agent")
        self.registry = self._initialize_registry()
        self.warehouse = FraguaWarehouse(name=f"{name}_warehouse")
        self.step_index = FraguaStepIndex()

    def _initialize_registry(self) -> FraguaRegistry:
        """
        Create and preload the default registry sets.
        """
        return FraguaRegistry(
            sets={
                "pipelines": FraguaSet("pipelines", step_enabled=False),
            }
        )

    # -------------------- Public API -------------------- #

    def create_set(self, name: str, *, step_enabled: bool = True) -> None:
        """
        Create a new registry set.

        Parameters
        ----------
        name:
            Name of the registry set.
        step_enabled:
            Whether callables registered in this set should
            generate FraguaStepBuilder templates.
        """
        if self.registry.get_set(name) is not None:
            raise ValueError(f"Registry set already exists: {name}")

        self.registry.add_set(
            FraguaSet(
                name=name,
                step_enabled=step_enabled,
            )
        )

    def create_transform_steps(
        self,
        *,
        step_names: Iterable[str],
        step_prefix: str,
        start_from: str | None,
    ) -> List[FraguaStep]:
        """
        Generate a sequence of FraguaStep objects using the environment's StepIndex,
        chaining them automatically.
        """
        steps: list[FraguaStep] = []
        previous_step_name: str | None = start_from

        for index, step_name in enumerate(step_names, start=1):
            builder = self.step_index.get(step_name)
            if builder is None:
                raise ValueError(f"Step not found in StepIndex: {step_name}")

            save_as = f"{step_prefix}_step_{index}"

            builder = builder.with_params().with_save_as(save_as)

            if previous_step_name is not None:
                builder = builder.with_use(previous_step_name)

            step = builder.build()

            steps.append(step)
            previous_step_name = save_as

        return steps

    def create_pipeline(self, name: str) -> FraguaPipelineBuilder:
        """
        Create a pipeline builder bound to this environment.

        Parameters
        ----------
        name:
            Name of the pipeline to be built.

        Returns
        -------
        FraguaPipelineBuilder
            A new pipeline builder instance.
        """
        if self.registry.get_set("pipelines") is None:
            raise RuntimeError("Pipelines registry set is not initialized")

        return FraguaPipelineBuilder(name)

    def register(
        self,
        item: Callable[..., Any] | FraguaPipeline,
        *,
        set_name: str | None = None,
        name: str | None = None,
    ) -> None:
        """
        Register a function or pipeline in the environment.
        """
        if isinstance(item, FraguaPipeline):
            target_set = self._get_registry_set("pipelines")
            item_name = name or item.name

        elif callable(item):
            if not set_name:
                raise ValueError("set_name is required when registering callables")

            target_set = self._get_registry_set(set_name)
            item_name = name or item.__name__

        else:
            raise TypeError(
                "Only callables or FraguaPipeline instances can be registered"
            )

        registered = target_set.register(item_name, item)
        if not registered:
            raise ValueError(
                f"Item '{item_name}' is already registered in set '{target_set.name}'"
            )

        self.step_index.register(
            name=item_name,
            builder=FraguaStepBuilder(
                set_name=target_set.name,
                function=item_name,
            ),
        )

    def run(self, pipeline: FraguaPipeline | str) -> FraguaBox:
        """
        Execute a pipeline by instance or by registered name.
        """
        resolved_pipeline = self._resolve_pipeline(pipeline)
        box = self.agent.run_pipeline(
            pipeline=resolved_pipeline,
            registry=self.registry,
        )
        self.warehouse.store(box)
        return box

    def compile_pipeline(self, definition: Dict[str, Any]) -> FraguaPipeline:
        """
        Compile a declarative pipeline definition into a FraguaPipeline.
        """
        self._validate_pipeline_definition(definition)

        expanded_steps: list[dict[str, Any]] = []

        # 1. Expand macros into concrete step definitions
        for step in definition["steps"]:
            if self._is_macro(step):
                macro_steps = self._expand_macro(step)
                expanded_steps.extend(macro_steps)
            else:
                expanded_steps.append(step)

        # 2. Normalize all steps (macros are gone at this point)
        normalized_steps = [self._normalize_step(step) for step in expanded_steps]

        # 3. Validate compiled structure
        self._validate_step_dependencies(normalized_steps)
        self._validate_registry_bindings(normalized_steps)

        # 4. Compile steps into FraguaStep
        compiled_steps = [self._compile_step(step) for step in normalized_steps]

        # 5. Build pipeline
        pipeline = FraguaPipeline(name=definition["name"])
        pipeline.add(compiled_steps)

        return pipeline

    # -------------------- Helpers -------------------- #

    def _get_registry_set(self, set_name: str) -> FraguaSet:
        target_set = self.registry.get_set(set_name)
        if target_set is None:
            raise ValueError(f"Unknown registry set: {set_name}")
        return target_set

    def _resolve_pipeline(self, pipeline: FraguaPipeline | str) -> FraguaPipeline:
        if isinstance(pipeline, FraguaPipeline):
            return pipeline

        pipeline_set = self._get_registry_set("pipelines")
        resolved = pipeline_set.get(pipeline)

        if resolved is None:
            raise ValueError(f"Pipeline not found: {pipeline}")

        if not isinstance(resolved, FraguaPipeline):
            raise TypeError(f"Registered item '{pipeline}' is not a FraguaPipeline")

        return resolved

    def _normalize_step(self, raw_step: Dict) -> Dict:
        if not isinstance(raw_step, dict):
            raise ValueError("Each step must be a dictionary.")

        if "set" not in raw_step or "function" not in raw_step:
            raise ValueError("Each step must define 'set' and 'function'.")

        return {
            "set": raw_step["set"],
            "function": raw_step["function"],
            "params": raw_step.get("params", {}),
            "save_as": raw_step.get("save_as"),
            "use": raw_step.get("use"),
        }

    def _validate_step_dependencies(self, steps: List[Dict]) -> None:
        available_keys = set()

        for step in steps:
            use = step.get("use")
            save_as = step.get("save_as")

            if use and use not in available_keys:
                raise ValueError(f"Step uses undefined result '{use}'.")

            if save_as:
                if save_as in available_keys:
                    raise ValueError(f"Duplicate save_as key '{save_as}'.")
                available_keys.add(save_as)

    def _validate_registry_bindings(self, steps: List[Dict]) -> None:
        for step in steps:
            function_set = self.registry.get_set(step["set"])
            if function_set is None:
                raise ValueError(f"Registry set not found: {step['set']}")

            fn = function_set.get_function(step["function"])
            if fn is None:
                raise ValueError(
                    f"Function '{step['function']}' not found in set '{step['set']}'"
                )

    def _validate_pipeline_definition(self, definition: Dict[str, Any]) -> None:
        if not isinstance(definition, dict):
            raise ValueError("Pipeline definition must be a dictionary.")

        if "name" not in definition:
            raise ValueError("Pipeline definition must include a 'name'.")

        if "steps" not in definition:
            raise ValueError("Pipeline definition must include 'steps'.")

        if not isinstance(definition["steps"], list):
            raise ValueError("'steps' must be a list.")

        if not definition["steps"]:
            raise ValueError("Pipeline must contain at least one step.")

    def _compile_step(self, step: Dict) -> FraguaStep:
        function_set = self.registry.get_set(step["set"])

        if function_set is None:
            raise ValueError("Function set not found.")

        if not function_set.step_enabled:
            return FraguaStep(
                set_name=step["set"],
                function=step["function"],
                params=step["params"],
                save_as=step["save_as"],
                use=step["use"],
            )

        builder = FraguaStepBuilder(
            set_name=step["set"],
            function=step["function"],
        )

        if step["params"]:
            builder.with_params(**step["params"])

        if step["save_as"]:
            builder.with_save_as(step["save_as"])

        if step["use"]:
            builder.with_use(step["use"])

        return builder.build()

    def _compile_macro(self, macro_def: dict) -> list[FraguaStep]:
        macro_name = macro_def["macro"]

        if macro_name != "transform_chain":
            raise ValueError(f"Unknown macro: {macro_name}")

        return self.create_transform_steps(
            step_names=macro_def["step_names"],
            step_prefix=macro_def["step_prefix"],
            start_from=macro_def.get("start_from"),
        )

    def _is_macro(self, step_def: Dict[str, Any]) -> bool:
        """
        Return True if the step definition represents a macro expansion.
        """
        return "macro" in step_def

    def _expand_macro(self, macro_def: Dict[str, Any]) -> list[Dict[str, Any]]:
        steps = self.create_transform_steps(
            step_names=macro_def["step_names"],
            step_prefix=macro_def["step_prefix"],
            start_from=macro_def.get("start_from"),
        )

        final_save_as = macro_def.get("save_as")

        expanded_steps = []

        for index, step in enumerate(steps):
            is_last = index == len(steps) - 1

            expanded_steps.append(
                {
                    "set": step.set_name,
                    "function": step.function,
                    "params": step.params,
                    "use": step.use,
                    "save_as": (
                        final_save_as if is_last and final_save_as else step.save_as
                    ),
                }
            )

        return expanded_steps
