"""Fragua execution environment.

Defines the orchestration layer for executing ETL functions
using a single agent, a function registry and a runtime warehouse.
"""

from typing import Any, Callable, Tuple

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
        """Create and preload the default registry sets."""
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

        The target registry set and item name are inferred
        from the provided object.
        """
        set_name, item_name = self._resolve_registration_target(item, name)
        target_set = self._get_registry_set(set_name)
        self._register_item(target_set, item_name, item)

    def run(self, pipeline: FraguaPipeline | str) -> FraguaBox:
        """
        Execute a pipeline by instance or by registered name.

        The resulting execution box is persisted in the warehouse.
        """
        resolved_pipeline = self._resolve_pipeline(pipeline)
        box = self._execute_pipeline(resolved_pipeline)
        self._store_execution_result(box)
        return box

    # -------------------- Registration helpers -------------------- #

    def _resolve_registration_target(
        self,
        item: Callable[..., Any] | FraguaPipeline,
        name: str | None,
    ) -> Tuple[str, str]:
        """
        Determine the registry set name and item name
        based on the provided object.
        """
        if isinstance(item, FraguaPipeline):
            return "pipelines", name or item.name

        if callable(item):
            return "functions", name or item.__name__

        raise TypeError("Only callables or FraguaPipeline instances can be registered")

    def _get_registry_set(self, set_name: str) -> FraguaSet:
        """
        Retrieve a registry set by name or fail fast if it does not exist.
        """
        target_set = self.registry.get_set(set_name)
        if target_set is None:
            raise ValueError(f"Unknown registry set: {set_name}")
        return target_set

    def _register_item(
        self,
        target_set: FraguaSet,
        item_name: str,
        item: Callable[..., Any] | FraguaPipeline,
    ) -> None:
        """
        Register an item in the given registry set.

        Raises if the item name already exists.
        """
        registered = target_set.register(item_name, item)
        if not registered:
            raise ValueError(
                f"{target_set.name[:-1].capitalize()} '{item_name}' is already registered"
            )

    # -------------------- Execution helpers -------------------- #

    def _resolve_pipeline(
        self,
        pipeline: FraguaPipeline | str,
    ) -> FraguaPipeline:
        """
        Resolve a pipeline either directly or from the registry by name.
        """
        if isinstance(pipeline, FraguaPipeline):
            return pipeline

        if isinstance(pipeline, str):
            pipeline_set = self._get_registry_set("pipelines")
            resolved = pipeline_set.get(pipeline)

            if resolved is None:
                raise ValueError(f"Pipeline not found: {pipeline}")

            if not isinstance(resolved, FraguaPipeline):
                raise TypeError(f"Registered item '{pipeline}' is not a FraguaPipeline")

            return resolved

        raise TypeError(
            "run() expects a FraguaPipeline instance or a registered pipeline name"
        )

    def _execute_pipeline(self, pipeline: FraguaPipeline) -> FraguaBox:
        """
        Execute the pipeline using the environment agent.
        """
        return self.agent.run_pipeline(
            pipeline=pipeline,
            registry=self.registry,
        )

    def _store_execution_result(self, box: FraguaBox) -> None:
        """
        Persist the execution result in the runtime warehouse.
        """
        self.warehouse.store(box)
