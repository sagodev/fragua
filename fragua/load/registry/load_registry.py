"""Load Registry Class."""

from typing import Any, Dict, cast
from fragua.core.registry import FraguaRegistry
from fragua.load.registry.load_sets import (
    LoadAgentSet,
    LoadFunctionSet,
    LoadParamsSet,
    LoadStyleSet,
)


class LoadRegistry(FraguaRegistry):
    """
    Registry for the *load* action.

    This registry centralizes and organizes all components required
    to execute load operations within the Fragua ETL framework.

    It groups and exposes:
    - Load parameter classes
    - Load style classes
    - Load function classes
    - Load agent classes

    Each group is stored internally as a dedicated FraguaSet and can
    be accessed through typed properties.
    """

    def __init__(self, registry_name: str, fg_config: bool) -> None:
        """
        Initialize the LoadRegistry instance.

        Args:
            registry_name (str):
                Logical name of the registry.
            fg_config (bool):
                Flag indicating whether the registry should be initialized
                using Fragua configuration rules.
        """
        super().__init__(registry_name)
        self._initialize_sets(fg_config)

    def _initialize_sets(self, fg_config: bool) -> None:
        """
        Initialize and register all load-related sets.

        This method creates the parameter, style, function and agent
        sets associated with the *load* action and registers them
        within the registry.
        """
        load_fg_sets = {
            "params": LoadParamsSet(fg_config),
            "styles": LoadStyleSet(fg_config),
            "functions": LoadFunctionSet(fg_config),
            "agents": LoadAgentSet(),
        }

        for name_set, cls_set in load_fg_sets.items():
            self.create_set(name_set, cls_set)

    @property
    def params(self) -> LoadParamsSet:
        """
        Access the set of registered load parameter classes.

        Returns:
            LoadParamsSet:
                Collection of parameter definitions for load styles.
        """
        return cast(LoadParamsSet, self.get_sets()["params"])

    @property
    def functions(self) -> LoadFunctionSet:
        """
        Access the set of registered load function classes.

        Returns:
            LoadFunctionSet:
                Collection of executable load functions.
        """
        return cast(LoadFunctionSet, self.get_sets()["functions"])

    @property
    def styles(self) -> LoadStyleSet:
        """
        Access the set of registered load style classes.

        Returns:
            LoadStyleSet:
                Collection of load styles that orchestrate load execution.
        """
        return cast(LoadStyleSet, self.get_sets()["styles"])

    @property
    def agents(self) -> LoadAgentSet:
        """
        Access the set of registered load agent classes.

        Returns:
            LoadAgentSet:
                Collection of agents responsible for executing load workflows.
        """
        return cast(LoadAgentSet, self.get_sets()["agents"])

    def summary(self) -> Dict[str, Any]:
        """
        Return a structured summary of all load components.

        This method aggregates the summaries of each load set
        (params, agents, functions, styles) into a single structured object.


        Returns:
            Dict([str, Any]):
                A dictionary with the following structure:
                - params (dict): Summary of the load params set
                - functions (dict): Summary of load functions set
                - styles (dict): Summary of the load styles set
                - agents (dict): Summary of the load agents set
        """
        load_summaries = {
            "params": self.params.summary(),
            "functions": self.functions.summary(),
            "styles": self.styles.summary(),
            "agents": self.agents.summary(),
        }
        return load_summaries
