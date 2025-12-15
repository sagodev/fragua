"""Extract Registry Class."""

from typing import Any, Dict, cast
from fragua.core.registry import FraguaRegistry
from fragua.extract.registry.extract_sets import (
    ExtractAgentSet,
    ExtractFunctionSet,
    ExtractParamsSet,
    ExtractStyleSet,
)


class ExtractRegistry(FraguaRegistry):
    """
    Registry that groups all extract-related components.

    This registry centralizes the configuration and discovery of:
    - Extract parameter schemas
    - Extract styles
    - Extract functions
    - Extract agents

    It acts as the single entry point for all components associated
    with the `extract` action within a Fragua environment.
    """

    def __init__(self, registry_name: str, fg_config: bool) -> None:
        """
        Initialize the extract registry.

        Args:
            registry_name: Logical name of the registry.
            fg_config: Flag indicating whether default Fragua
                components should be auto-registered.
        """
        super().__init__(registry_name)
        self._initialize_sets(fg_config)

    def _initialize_sets(self, fg_config: bool) -> None:
        """
        Initialize and register extract-related component sets.

        Args:
            fg_config: Controls whether built-in Fragua components
                are loaded into each set.
        """
        extract_fg_sets = {
            "params": ExtractParamsSet(fg_config),
            "styles": ExtractStyleSet(fg_config),
            "functions": ExtractFunctionSet(fg_config),
            "agents": ExtractAgentSet(),
        }

        for name_set, cls_set in extract_fg_sets.items():
            self.create_set(name_set, cls_set)

    @property
    def params(self) -> ExtractParamsSet:
        """
        Access the set containing extract parameter schemas.

        Returns:
            ExtractParamsSet instance.
        """
        return cast(ExtractParamsSet, self.get_sets()["params"])

    @property
    def functions(self) -> ExtractFunctionSet:
        """
        Access the set containing extract functions.

        Returns:
            ExtractFunctionSet instance.
        """
        return cast(ExtractFunctionSet, self.get_sets()["functions"])

    @property
    def styles(self) -> ExtractStyleSet:
        """
        Access the set containing extract styles.

        Returns:
            ExtractStyleSet instance.
        """
        return cast(ExtractStyleSet, self.get_sets()["styles"])

    @property
    def agents(self) -> ExtractAgentSet:
        """
        Access the set containing extract agents.

        Returns:
            ExtractAgentSet instance.
        """
        return cast(ExtractAgentSet, self.get_sets()["agents"])

    def summary(self) -> Dict[str, Any]:
        """
        Return a structured summary of all extract components.

        This method aggregates the summaries of each extract set
        (params, agents, functions, styles) into a single structured object.


        Returns:
            Dict([str, Any]):
                A dictionary with the following structure:
                - params (dict): Summary of the extract params set
                - functions (dict): Summary of extract functions set
                - styles (dict): Summary of the extract styles set
                - agents (dict): Summary of the extract agents set
        """
        extract_summaries = {
            "params": self.params.summary(),
            "functions": self.functions.summary(),
            "styles": self.styles.summary(),
            "agents": self.agents.summary(),
        }

        return extract_summaries
