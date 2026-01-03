"""Fragua execution environment.

Defines the orchestration layer for executing ETL functions
using a single agent, a function registry and a runtime warehouse.
"""

from typing import Any, Callable

from fragua.core.agent import FraguaAgent
from fragua.core.pipeline import FraguaPipeline
from fragua.core.registry import FraguaRegistry
from fragua.core.warehouse import FraguaWarehouse
from fragua.core.set import FraguaSet


class FraguaEnvironment:
    """
    Execution environment for Fragua.

    An environment owns exactly one agent, one function registry
    and one runtime warehouse.
    """

    def __init__(self, name: str) -> None:
        self.name = name

        self.agent = FraguaAgent(name=f"{name}_agent")
        self.registry = self._initialize_registry()
        self.warehouse = FraguaWarehouse(name=f"{name}_warehouse")

    def _initialize_registry(self) -> FraguaRegistry:
        sets = {
            "extract": FraguaSet("extract"),
            "transform": FraguaSet("transform"),
            "load": FraguaSet("load"),
        }
        return FraguaRegistry(sets=sets)

    # -------------------- Public API -------------------- #

    def register_function(
        self,
        action: str,
        fn: Callable[..., Any],
        *,
        name: str | None = None,
    ) -> None:
        """
        Register a function under an action set.
        """
        function_name = name or fn.__name__
        function_set = self.registry.get_set(action)

        if function_set is None:
            raise ValueError(f"Unknown action set: {action}")

        function_set.register(function_name, fn)

    def run(self, pipeline: FraguaPipeline) -> FraguaWarehouse:
        """
        Execute a pipeline using the environment's agent.

        The environment delegates execution to the agent
        and exposes the populated warehouse as execution output.
        """
        self.agent.run_pipeline(
            pipeline=pipeline,
            registry=self.registry,
            warehouse=self.warehouse,
        )

        return self.warehouse
