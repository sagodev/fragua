"""Fragua Environment Class."""

from typing import Any, Callable, Dict, Iterable, List, Optional, Union

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

    name: str
    agent: FraguaAgent
    registry: FraguaRegistry
    warehouse: FraguaWarehouse
    step_index: FraguaStepIndex

    def __init__(self, name: str) -> None:
        self.name = name
        self.agent = FraguaAgent(name=f"{name}_agent")
        self.registry = self._initialize_registry()
        self.warehouse = FraguaWarehouse(name=f"{name}_warehouse")
        self.step_index = FraguaStepIndex()

    def _initialize_registry(self) -> FraguaRegistry:
        return FraguaRegistry(
            sets={
                "pipelines": FraguaSet("pipelines", step_enabled=False),
            }
        )

    # -------------------- Public API -------------------- #

    def create_set(self, name: str, *, step_enabled: bool = True) -> None:
        """
        Create a new registry set.

        Args:
            name: Name of the set to create.
            step_enabled: Whether steps can be created from this set.
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
        start_from: Optional[str],
    ) -> List[FraguaStep]:
        """
        Create a chain of transform steps.

        Args:
            step_names: Names of the steps to create from the step index.
            step_prefix: Prefix for naming saved results.
            start_from: Optional name of the step to start from.

        Returns:
            List of created FraguaStep instances.
        """
        steps: List[FraguaStep] = []
        previous_step_name: Optional[str] = start_from

        for index, step_name in enumerate(step_names, start=1):
            builder: Optional[FraguaStepBuilder] = self.step_index.get(step_name)
            if builder is None:
                raise ValueError(f"Step not found in StepIndex: {step_name}")

            save_as: str = f"{step_prefix}_step_{index}"
            builder = builder.with_params().with_save_as(save_as)

            if previous_step_name is not None:
                builder = builder.with_use(previous_step_name)

            step: FraguaStep = builder.build()
            steps.append(step)
            previous_step_name = save_as

        return steps

    def create_pipeline(self, name: str) -> FraguaPipelineBuilder:
        """
        Create a new pipeline builder.

        Args:
            name: Name of the pipeline.

        Returns:
            FraguaPipelineBuilder instance for constructing the pipeline.
        """
        if self.registry.get_set("pipelines") is None:
            raise RuntimeError("Pipelines registry set is not initialized")

        return FraguaPipelineBuilder(name)

    def register(
        self,
        item: Union[Callable[..., Any], FraguaPipeline],
        *,
        set_name: Optional[str] = None,
        name: Optional[str] = None,
    ) -> None:
        """
        Register an item in the environment's registry.

        Args:
            item: Callable or FraguaPipeline to register.
            set_name: Name of the registry set (required for callables).
            name: Optional custom name for the item.
        """
        if isinstance(item, FraguaPipeline):
            target_set: FraguaSet = self._get_registry_set("pipelines")
            item_name: str = name or item.name
        elif callable(item):
            if not set_name:
                raise ValueError("set_name is required when registering callables")
            target_set = self._get_registry_set(set_name)
            item_name = name or item.__name__
        else:
            raise TypeError(
                "Only callables or FraguaPipeline instances can be registered"
            )

        registered: bool = target_set.register(item_name, item)
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

    def run(self, pipeline: Union[FraguaPipeline, str]) -> FraguaBox:
        """
        Execute a pipeline and return the result.

        Args:
            pipeline: FraguaPipeline instance or name of registered pipeline.

        Returns:
            FraguaBox containing the pipeline execution results.
        """
        resolved_pipeline: FraguaPipeline = self._resolve_pipeline(pipeline)
        box: FraguaBox = self.agent.run_pipeline(
            pipeline=resolved_pipeline,
            registry=self.registry,
        )
        self.warehouse.store(box)
        return box

    def compile_pipeline(self, definition: Dict[str, Any]) -> FraguaPipeline:
        """
        Compile a pipeline from a dictionary definition.

        Args:
            definition: Dictionary containing pipeline name and steps.

        Returns:
            Compiled FraguaPipeline ready for execution.
        """
        self._validate_pipeline_definition(definition)

        expanded_steps: List[Dict[str, Any]] = []

        for step in definition["steps"]:
            if self._is_macro(step):
                macro_steps: List[Dict[str, Any]] = self._expand_macro(step)
                expanded_steps.extend(macro_steps)
            else:
                expanded_steps.append(step)

        normalized_steps: List[Dict[str, Any]] = [
            self._normalize_step(step) for step in expanded_steps
        ]

        self._validate_step_dependencies(normalized_steps)
        self._validate_registry_bindings(normalized_steps)

        compiled_steps: List[FraguaStep] = [
            self._compile_step(step) for step in normalized_steps
        ]

        pipeline: FraguaPipeline = FraguaPipeline(name=definition["name"])
        pipeline.add(compiled_steps)

        return pipeline

    # -------------------- Helpers -------------------- #

    def _get_registry_set(self, set_name: str) -> FraguaSet:
        target_set: Optional[FraguaSet] = self.registry.get_set(set_name)
        if target_set is None:
            raise ValueError(f"Unknown registry set: {set_name}")
        return target_set

    def _resolve_pipeline(self, pipeline: Union[FraguaPipeline, str]) -> FraguaPipeline:
        if isinstance(pipeline, FraguaPipeline):
            return pipeline

        pipeline_set: FraguaSet = self._get_registry_set("pipelines")

        resolved: Optional[FraguaPipeline] = pipeline_set.get_pipeline(pipeline)

        if resolved is None:
            raise ValueError(f"Pipeline not found: {pipeline}")

        if not isinstance(resolved, FraguaPipeline):
            raise TypeError(f"Registered item '{pipeline}' is not a FraguaPipeline")

        return resolved

    def _normalize_step(self, raw_step: Dict[str, Any]) -> Dict[str, Any]:
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

    def _validate_step_dependencies(self, steps: List[Dict[str, Any]]) -> None:
        available_keys: set[str] = set()

        for step in steps:
            use: Optional[str] = step.get("use")
            save_as: Optional[str] = step.get("save_as")

            if use and use not in available_keys:
                raise ValueError(f"Step uses undefined result '{use}'.")

            if save_as:
                if save_as in available_keys:
                    raise ValueError(f"Duplicate save_as key '{save_as}'.")
                available_keys.add(save_as)

    def _validate_registry_bindings(self, steps: List[Dict[str, Any]]) -> None:
        for step in steps:
            function_set: Optional[FraguaSet] = self.registry.get_set(step["set"])
            if function_set is None:
                raise ValueError(f"Registry set not found: {step['set']}")

            fn: Optional[Callable[..., Any]] = function_set.get_function(
                step["function"]
            )
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

    def _compile_step(self, step: Dict[str, Any]) -> FraguaStep:
        function_set: Optional[FraguaSet] = self.registry.get_set(step["set"])
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

        builder: FraguaStepBuilder = FraguaStepBuilder(
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

    def _is_macro(self, step_def: Dict[str, Any]) -> bool:
        return "macro" in step_def

    def _expand_macro(self, macro_def: Dict[str, Any]) -> List[Dict[str, Any]]:
        steps: List[FraguaStep] = self.create_transform_steps(
            step_names=macro_def["step_names"],
            step_prefix=macro_def["step_prefix"],
            start_from=macro_def.get("start_from"),
        )

        final_save_as: Optional[str] = macro_def.get("save_as")

        expanded_steps: List[Dict[str, Any]] = []

        for index, step in enumerate(steps):
            is_last: bool = index == len(steps) - 1
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
