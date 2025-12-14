"""Actions class."""

from typing import Any, Dict
from fragua.core.component import FraguaComponent
from fragua.extract.registry.extract_registry import ExtractRegistry
from fragua.load.registry.load_registry import LoadRegistry
from fragua.transform.registry.transform_registry import TransformRegistry


class FraguaActions(FraguaComponent):
    """
    Centralized container for ETL action registries.

    This component groups and manages the registries associated with
    each ETL action type (extract, transform, load). It acts as a
    single access point for resolving action-specific components
    within the Fragua Environment.
    """

    def __init__(self, fg_config: bool) -> None:
        """
        Initialize the FraguaActions component and its registries.

        Args:
            fg_config: Flag indicating whether the environment is
                running in configuration mode.
        """
        super().__init__(component_name="fragua_actions")
        self.fg_config = fg_config
        self._extract = self._initialize_extract_registry()
        self._transform = self._initialize_transform_registry()
        self._load = self._initialize_load_registry()

    def _initialize_extract_registry(self) -> ExtractRegistry:
        """
        Create and initialize the Extract registry.

        Returns:
            An initialized ExtractRegistry instance.
        """
        reg_name = "extract"
        extract_registry = ExtractRegistry(reg_name, self.fg_config)
        return extract_registry

    def _initialize_transform_registry(self) -> TransformRegistry:
        """
        Create and initialize the Transform registry.

        Returns:
            An initialized TransformRegistry instance.
        """
        reg_name = "transform"
        transform_registry = TransformRegistry(reg_name, self.fg_config)
        return transform_registry

    def _initialize_load_registry(self) -> LoadRegistry:
        """
        Create and initialize the Load registry.

        Returns:
            An initialized LoadRegistry instance.
        """
        reg_name = "load"
        load_registry = LoadRegistry(reg_name, self.fg_config)
        return load_registry

    @property
    def extract(self) -> ExtractRegistry:
        """
        Access the Extract action registry.

        Returns:
            The ExtractRegistry instance.
        """
        return self._extract

    @property
    def transform(self) -> TransformRegistry:
        """
        Access the Transform action registry.

        Returns:
            The TransformRegistry instance.
        """
        return self._transform

    @property
    def load(self) -> LoadRegistry:
        """
        Access the Load action registry.

        Returns:
            The LoadRegistry instance.
        """
        return self._load

    def summary(self) -> Dict[str, Any]:
        """
        Generate a consolidated summary of all action registries.

        Returns:
            A dictionary containing the summary of extract, transform,
            and load registries.
        """
        return {
            "extract": self.extract.summary(),
            "transform": self.transform.summary(),
            "load": self.load.summary(),
        }
