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
            cls = cast(ExtractParams, cls)
            self.add(name, cls)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Return a structured summary of all extract parameter schemas.
        """
        result: Dict[str, Dict[str, Any]] = {}

        if not self.fg_config:
            return result

        for name, cls in self.get_all().items():
            cls = cast(Type[ExtractParams], cls)
            obj = cls(name)
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
            cls = cast(ExtractFunction, cls)
            self.add(name, cls)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Return a structured summary of all extract functions.
        """
        result: Dict[str, Dict[str, Any]] = {}

        if not self.fg_config:
            return result

        for name, cls in self.get_all().items():
            cls = cast(Type[ExtractFunction], cls)
            obj = cls()
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
            cls = cast(ExtractStyle, cls)
            self.add(name, cls)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Return a structured summary of all extract styles.
        """
        result: Dict[str, Dict[str, Any]] = {}

        if not self.fg_config:
            return result

        for name, cls in self.get_all().items():
            cls = cast(Type[ExtractStyle], cls)
            obj = cls()
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

        for name, agent in self.get_all().items():
            agent = cast(Extractor, agent)
            result[name] = agent.summary()

        return result
