"""Load Sections Module."""

from typing import Any, Dict, cast
import pandas as pd
from fragua.core.section_registry import SectionRegistry
from fragua.load import (
    LOAD_FUNCTION_CLASSES,
    LOAD_PARAMS_CLASSES,
    LOAD_STYLE_CLASSES,
    LoadStyle,
    LoadFunction,
    LoadParams,
    Loader,
)


class LoadParamsSection(SectionRegistry):
    """Section containing load parameters classes."""

    def __init__(self, section_name: str = "params") -> None:
        super().__init__(section_name)
        self._initialize_params()

    def _initialize_params(self) -> None:
        """Load all predefined load parameter classes into the section."""
        for name, cls in LOAD_PARAMS_CLASSES.items():
            self.create_entry(name, cls)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Return a structured summary of all load parameter classes.
        """
        result: Dict[str, Dict[str, Any]] = {}

        for name, cls in self.get_entries().items():
            obj = cls.__new__(cls)
            obj = cast(LoadParams, obj)
            df = pd.DataFrame({})
            LoadParams.__init__(obj, style=name, data=df)

            data = obj.summary()

            result[name] = data

        return result


class LoadFunctionSection(SectionRegistry):
    """Load functions section."""

    def __init__(self, section_name: str = "functions") -> None:
        super().__init__(section_name)
        self._initialize_functions()

    def _initialize_functions(self) -> None:
        """Load all predefined load functions into the section."""
        for name, cls in LOAD_FUNCTION_CLASSES.items():
            self.create_entry(name, cls)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Return a structured summary of all load functions.
        """
        result: Dict[str, Dict[str, Any]] = {}

        for name, cls in self.get_entries().items():
            df = pd.DataFrame({})

            params = LoadParams.__new__(LoadParams)
            LoadParams.__init__(params, style=name, data=df)

            obj = cls.__new__(cls)
            obj = cast(LoadFunction, obj)
            obj.name = name
            obj.params = params

            data = obj.summary()

            result[name] = data

        return result


class LoadStyleSection(SectionRegistry):
    """Section that stores all load style classes."""

    def __init__(self, section_name: str = "styles") -> None:
        super().__init__(section_name)
        self._initialize_styles()

    def _initialize_styles(self) -> None:
        """Load predefined load style classes into the section."""
        for name, cls in LOAD_STYLE_CLASSES.items():
            self.create_entry(name, cls)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Summary of all load style classes.
        """
        result: Dict[str, Dict[str, Any]] = {}

        for name, cls in self.get_entries().items():

            obj = cls.__new__(cls)
            obj = cast(LoadStyle, obj)
            data = obj.summary()

            result[name] = data

        return result


class LoadAgentSection(SectionRegistry):
    """Load agents section."""

    def __init__(self, section_name="agents"):
        super().__init__(section_name)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """Load agents section summary."""
        result: Dict[str, Dict[str, Any]] = {}

        for name, cls in self.get_entries().items():

            obj = cls.__new__(cls)
            obj = cast(Loader, obj)
            data = obj.summary()

            result[name] = data

        return result
