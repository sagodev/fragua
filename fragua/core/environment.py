"""Fragua execution environment.

Defines the orchestration layer for executing ETL functions
using a single agent, a function registry and a runtime warehouse.
"""

from typing import Any, Callable

from fragua.core.agent import FraguaAgent
from fragua.core.box import FraguaBox
from fragua.core.pipeline import FraguaPipeline
from fragua.core.registry import FraguaRegistry
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

    def _initialize_registry(self) -> FraguaRegistry:
        sets = {
            "pipelines": FraguaSet("pipelines"),
            "functions": FraguaSet("functions"),
        }
        return FraguaRegistry(sets=sets)

    # -------------------- Public API -------------------- #

    def register(
        self,
        item: Callable[..., Any] | FraguaPipeline,
        *,
        name: str | None = None,
    ) -> None:
        """
        Register a function or pipeline in the environment.

        The target set is inferred from the item type.
        """
        if isinstance(item, FraguaPipeline):
            set_name = "pipelines"
            item_name = name or item.name

        elif callable(item):
            set_name = "functions"
            item_name = name or item.__name__

        else:
            raise TypeError(
                "Only callables or FraguaPipeline instances can be registered"
            )

        target_set = self.registry.get_set(set_name)
        if target_set is None:
            raise ValueError(f"Unknown registry set: {set_name}")

        registered = target_set.register(item_name, item)
        if not registered:
            raise ValueError(
                f"{set_name[:-1].capitalize()} '{item_name}' is already registered"
            )

    def run(self, pipeline: FraguaPipeline | str) -> FraguaBox:
        """
        Execute a pipeline by instance or by registered name.
        """
        resolved_pipeline: FraguaPipeline

        if isinstance(pipeline, str):
            pipeline_set = self.registry.get_set("pipelines")
            if pipeline_set is None:
                raise ValueError("Pipeline registry set not found")

            resolved = pipeline_set.get(pipeline)
            if resolved is None:
                raise ValueError(f"Pipeline not found: {pipeline}")

            if not isinstance(resolved, FraguaPipeline):
                raise TypeError(f"Registered item '{pipeline}' is not a FraguaPipeline")

            resolved_pipeline = resolved

        elif isinstance(pipeline, FraguaPipeline):
            resolved_pipeline = pipeline

        else:
            raise TypeError(
                "run() expects a FraguaPipeline instance or a registered pipeline name"
            )

        box: FraguaBox = self.agent.run_pipeline(
            pipeline=resolved_pipeline,
            registry=self.registry,
        )

        self.warehouse.store(box)

        return box
