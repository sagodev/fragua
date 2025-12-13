"""Extract Sections Module."""

from typing import Any, Dict, Type, cast
from fragua.core.set import FraguaSet

from fragua.extract import (
    EXTRACT_FUNCTION_CLASSES,
    EXTRACT_PARAMS_CLASSES,
    EXTRACT_STYLE_CLASSES,
    ExtractStyle,
    ExtractFunction,
    ExtractParams,
    Extractor,
)


class ExtractParamsSet(FraguaSet):
    """Section containing extract parameters classes."""

    def __init__(self, fg_config: bool, section_name: str = "params") -> None:
        super().__init__(section_name)
        self.fg_config = fg_config
        self._initialize_params()

    def _initialize_params(self) -> None:
        """Load all predefined extract parameter classes into the section."""
        if self.fg_config:
            for name, cls in EXTRACT_PARAMS_CLASSES.items():
                cls = cast(ExtractParams, cls)
                self.add(name, cls)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Summary of all extract parameter classes.
        """
        result: Dict[str, Dict[str, Any]] = {}

        if self.fg_config:
            for name, cls in self.get_all().items():
                cls = cast(Type[ExtractParams], cls)
                obj = cls(name)

                result[name] = obj.summary()

        return result


class ExtractFunctionSet(FraguaSet):
    """Extract functions section."""

    def __init__(self, fg_config: bool, section_name: str = "functions") -> None:
        super().__init__(section_name)
        self.fg_config = fg_config
        self._initialize_functions()

    def _initialize_functions(self) -> None:
        """Load all predefined extract functions into the section."""
        if self.fg_config:
            for name, cls in EXTRACT_FUNCTION_CLASSES.items():
                cls = cast(ExtractFunction, cls)
                self.add(name, cls)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Summary of all extract functions.
        """
        result: Dict[str, Dict[str, Any]] = {}

        if self.fg_config:
            for name, cls in self.get_all().items():

                cls = cast(Type[ExtractFunction], cls)
                obj = cls()
                data = obj.summary()

                result[name] = data

        return result


class ExtractStyleSet(FraguaSet):
    """Section that stores all extract style classes."""

    def __init__(self, fg_config: bool, section_name: str = "styles") -> None:
        super().__init__(section_name)
        self.fg_config = fg_config
        self._initialize_styles()

    def _initialize_styles(self) -> None:
        """Load predefined extract style classes into the section."""
        if self.fg_config:
            for name, cls in EXTRACT_STYLE_CLASSES.items():
                cls = cast(ExtractStyle, cls)
                self.add(name, cls)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Summary of all extract style classes.
        """
        result: Dict[str, Dict[str, Any]] = {}

        if self.fg_config:
            for name, cls in self.get_all().items():

                cls = cast(Type[ExtractStyle], cls)
                obj = cls()
                data = obj.summary()

                result[name] = data

        return result


class ExtractAgentSet(FraguaSet):
    """Extract agents section."""

    def __init__(self, section_name="agents"):
        super().__init__(section_name)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Summary of all extract agentsclasses.
        """
        result: Dict[str, Dict[str, Any]] = {}

        for name, instance in self.get_all().items():

            obj = cast(Extractor, instance)
            data = obj.summary()

            result[name] = data

        return result
