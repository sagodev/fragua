"""Actions class."""

from typing import Any, Dict
from fragua.core.component import FraguaComponent
from fragua.extract.registry.extract_registry import ExtractRegistry
from fragua.load.registry.load_registry import LoadRegistry
from fragua.transform.registry.transform_registry import TransformRegistry


class FraguaActions(FraguaComponent):
    """
    Actions class
    This class contain ETL registries.
    """

    def __init__(self, fg_config: bool) -> None:
        """Initialize Fragua action component."""
        super().__init__(component_name="fragua_actions")
        self.fg_config = fg_config
        self._extract = self._initialize_extract_registry()
        self._transform = self._initialize_transform_registry()
        self._load = self._initialize_load_registry()

    def _initialize_extract_registry(self) -> ExtractRegistry:
        """"""
        reg_name = "extract"
        extract_registry = ExtractRegistry(reg_name, self.fg_config)

        return extract_registry

    def _initialize_transform_registry(self) -> TransformRegistry:
        """"""
        reg_name = "transform"
        transform_registry = TransformRegistry(reg_name, self.fg_config)

        return transform_registry

    def _initialize_load_registry(self) -> LoadRegistry:
        """"""
        reg_name = "load"
        load_registry = LoadRegistry(reg_name, self.fg_config)

        return load_registry

    @property
    def extract(self) -> ExtractRegistry:
        """Retrive extract registry."""
        return self._extract

    @property
    def transform(self) -> TransformRegistry:
        """Retrive transform registry."""
        return self._transform

    @property
    def load(self) -> LoadRegistry:
        """Retrive load registry."""
        return self._load

    def summary(self) -> Dict[str, Any]:
        """Actions class summary."""
        return {
            "extract": self.extract.summary(),
            "transform": self.transform.summary(),
            "load": self.load.summary(),
        }
