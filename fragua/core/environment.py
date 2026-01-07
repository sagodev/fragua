"""Fragua execution environment.

Defines the orchestration layer for executing ETL functions
using a single agent, a registry and a runtime warehouse.
"""

from typing import Any, Callable, Iterable, List

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
