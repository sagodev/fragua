"""Extract Sections Module."""

from typing import Any, Dict, cast
from fragua.core.section_registry import SectionRegistry

from fragua.extract import (
    EXTRACT_FUNCTION_CLASSES,
    EXTRACT_PARAMS_CLASSES,
    EXTRACT_STYLE_CLASSES,
    ExtractStyle,
    ExtractFunction,
    ExtractParams,
    Extractor,
)


class ExtractParamsSection(SectionRegistry):
    """Section containing extract parameters classes."""

    def __init__(self, section_name: str = "params") -> None:
        super().__init__(section_name)
        self._initialize_params()

    def _initialize_params(self) -> None:
        """Load all predefined extract parameter classes into the section."""
        for name, cls in EXTRACT_PARAMS_CLASSES.items():
            self.create_entry(name, cls)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Return a structured summary of all extract parameter classes.
        """
        result: Dict[str, Dict[str, Any]] = {}

        for name, cls in self.get_entries().items():

            obj = cls.__new__(cls)
            obj = cast(ExtractParams, obj)
            ExtractParams.__init__(obj, style=name)

            data = obj.summary()

            result[name] = data

        return result


class ExtractFunctionSection(SectionRegistry):
    """Extract functions section."""

    def __init__(self, section_name: str = "functions") -> None:
        super().__init__(section_name)
        self._initialize_functions()

    def _initialize_functions(self) -> None:
        """Load all predefined extract functions into the section."""
        for name, cls in EXTRACT_FUNCTION_CLASSES.items():
            self.create_entry(name, cls)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Return a structured summary of all extract functions.
        """
        result: Dict[str, Dict[str, Any]] = {}

        for name, cls in self.get_entries().items():

            params = ExtractParams.__new__(ExtractParams)
            ExtractParams.__init__(params, style=name)

            obj = cls.__new__(cls)
            obj = cast(ExtractFunction, obj)
            obj.name = name
            obj.params = params

            data = obj.summary()

            result[name] = data

        return result


class ExtractStyleSection(SectionRegistry):
    """Section that stores all extract style classes."""

    def __init__(self, section_name: str = "styles") -> None:
        super().__init__(section_name)
        self._initialize_styles()

    def _initialize_styles(self) -> None:
        """Load predefined extract style classes into the section."""
        for name, cls in EXTRACT_STYLE_CLASSES.items():
            self.create_entry(name, cls)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Summary of all extract style classes.
        """
        result: Dict[str, Dict[str, Any]] = {}

        for name, cls in self.get_entries().items():

            obj = cls.__new__(cls)
            obj = cast(ExtractStyle, obj)
            data = obj.summary()

            result[name] = data

        return result


class ExtractAgentSection(SectionRegistry):
    """Extract agents section."""

    def __init__(self, section_name="agents"):
        super().__init__(section_name)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """Extract agents section summary."""
        result: Dict[str, Dict[str, Any]] = {}

        for name, cls in self.get_entries().items():

            obj = cls.__new__(cls)
            obj = cast(Extractor, obj)
            data = obj.summary()

            result[name] = data

        return result
