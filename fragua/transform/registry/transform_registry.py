"""
Transform Registry Class.

Provides centralized registration and access to all transformation-related
components in the Fragua ETL framework, including parameters, styles,
functions, and agents.
"""

from typing import Any, Dict, cast
from fragua.core.registry import FraguaRegistry
from fragua.transform.registry.transform_sets import (
    TransformAgentSet,
    TransformFunctionSet,
    TransformParamsSet,
    TransformStyleSet,
)


class TransformRegistry(FraguaRegistry):
    """
    Registry responsible for transformation components.

    This registry groups and manages all entities associated with the
    ``transform`` action, including:

    - Transformation parameter classes
    - Transformation styles
    - Transformation functions
    - Transformation agents

    It acts as the single entry point for discovering, summarizing,
    and resolving transformation behavior within an environment.
    """

    def __init__(self, registry_name: str, fg_config: bool) -> None:
        """
        Initialize the TransformRegistry.

        Args:
            registry_name (str):
                Logical name assigned to this registry instance.
            fg_config (bool):
                Flag indicating whether built-in Fragua components
                should be automatically registered.
        """
        super().__init__(registry_name)
        self._initialize_sets(fg_config)

    def _initialize_sets(self, fg_config: bool) -> None:
        """
        Initialize and register all transform-related sets.

        This method creates and registers the parameter, style,
        function, and agent sets required to support the
        ``transform`` action.
        """
        transform_fg_sets = {
            "params": TransformParamsSet(fg_config),
            "styles": TransformStyleSet(fg_config),
            "functions": TransformFunctionSet(fg_config),
            "agents": TransformAgentSet(),
        }

        for name_set, cls_set in transform_fg_sets.items():
            self.create_set(name_set, cls_set)

    @property
    def params(self) -> TransformParamsSet:
        """
        Access the set of registered transform parameter classes.

        Returns:
            TransformParamsSet:
                Set containing all available transformation parameters.
        """
        return cast(TransformParamsSet, self.get_sets()["params"])

    @property
    def functions(self) -> TransformFunctionSet:
        """
        Access the set of registered transform functions.

        Returns:
            TransformFunctionSet:
                Set containing all available transformation functions.
        """
        return cast(TransformFunctionSet, self.get_sets()["functions"])

    @property
    def styles(self) -> TransformStyleSet:
        """
        Access the set of registered transform styles.

        Returns:
            TransformStyleSet:
                Set containing all available transformation styles.
        """
        return cast(TransformStyleSet, self.get_sets()["styles"])

    @property
    def agents(self) -> TransformAgentSet:
        """
        Access the set of registered transform agents.

        Returns:
            TransformAgentSet:
                Set containing all available transformation agents.
        """
        return cast(TransformAgentSet, self.get_sets()["agents"])

    def summary(self) -> Dict[str, Any]:
        """
        Return a structured summary of all transform components.

        This method aggregates the summaries of each transform set
        (params, agents, functions, styles) into a single structured object.


        Returns:
            Dict([str, Any]):
                A dictionary with the following structure:
                - params (dict): Summary of the transform params set
                - functions (dict): Summary of transform functions set
                - styles (dict): Summary of the transform styles set
                - agents (dict): Summary of the transform agents set

        """
        transform_summaries = {
            "params": self.params.summary(),
            "functions": self.functions.summary(),
            "styles": self.styles.summary(),
            "agents": self.agents.summary(),
        }
        return transform_summaries
