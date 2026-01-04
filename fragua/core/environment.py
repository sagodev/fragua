"""Fragua execution environment.

Defines the orchestration layer for executing ETL functions
using a single agent, a registry and a runtime warehouse.
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
        """
        Create and preload the default registry sets.
        """
        return FraguaRegistry(
            sets={
                "pipelines": FraguaSet("pipelines"),
            }
        )

    # -------------------- Public API -------------------- #

    def create_set(self, name: str) -> None:
        """
        Create a new registry set.
        """
        if self.registry.get_set(name) is not None:
            raise ValueError(f"Registry set already exists: {name}")

        self.registry.add_set(FraguaSet(name))

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
