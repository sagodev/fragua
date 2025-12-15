"""Extract Sections Module."""

from typing import Any, Dict, cast
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
    """
    Set containing extract parameter schema classes.
    """

    def __init__(self, fg_config: bool, section_name: str = "params") -> None:
        super().__init__(section_name)
        self.fg_config = fg_config
        self._initialize_params()

    def _initialize_params(self) -> None:
        """
        Register built-in extract parameter classes.
        """
        if not self.fg_config:
            return

        for name, cls in EXTRACT_PARAMS_CLASSES.items():
            instance = cls(name)
            self.add(name, instance)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Return a structured summary of all extract parameter schemas.
        """
        result: Dict[str, Dict[str, Any]] = {}

        for name, instance in self.get_all().items():
            obj = cast(ExtractParams, instance)
            result[name] = obj.summary()

        return result


class ExtractFunctionSet(FraguaSet):
    """
    Set containing extract function classes.
    """

    def __init__(self, fg_config: bool, section_name: str = "functions") -> None:
        super().__init__(section_name)
        self.fg_config = fg_config
        self._initialize_functions()

    def _initialize_functions(self) -> None:
        """
        Register built-in extract functions.
        """
        if not self.fg_config:
            return

        for name, cls in EXTRACT_FUNCTION_CLASSES.items():
            instance = cls()
            self.add(name, instance)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Return a structured summary of all extract functions.
        """
        result: Dict[str, Dict[str, Any]] = {}

        for name, instance in self.get_all().items():
            obj = cast(ExtractFunction, instance)
            result[name] = obj.summary()

        return result


class ExtractStyleSet(FraguaSet):
    """
    Set containing extract style classes.
    """

    def __init__(self, fg_config: bool, section_name: str = "styles") -> None:
        super().__init__(section_name)
        self.fg_config = fg_config
        self._initialize_styles()

    def _initialize_styles(self) -> None:
        """
        Register built-in extract styles.
        """
        if not self.fg_config:
            return

        for name, cls in EXTRACT_STYLE_CLASSES.items():
            instance = cls()
            self.add(name, instance)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Return a structured summary of all extract styles.
        """
        result: Dict[str, Dict[str, Any]] = {}

        for name, instance in self.get_all().items():
            obj = cast(ExtractStyle[Any], instance)
            result[name] = obj.summary()

        return result


class ExtractAgentSet(FraguaSet):
    """
    Set containing extract agent instances.
    """

    def __init__(self, section_name: str = "agents") -> None:
        super().__init__(section_name)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Return a structured summary of all registered extract agents.
        """
        result: Dict[str, Dict[str, Any]] = {}

        for name, instance in self.get_all().items():
            agent = cast(Extractor[ExtractParams], instance)
            result[name] = agent.summary()

        return result
