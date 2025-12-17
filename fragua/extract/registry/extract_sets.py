"""
Extract Sections Module.

Defines the collection sets used to register and organize all extraction-
related components in the Fragua ETL framework, including parameters,
functions, styles, and agents.
"""

from typing import Any, Dict

from fragua.core.function import FraguaFunction
from fragua.core.set import FraguaSet
from fragua.core.params import FraguaParams
from fragua.core.style import FraguaStyle

from fragua.extract import (
    EXTRACT_FUNCTION_CLASSES,
    EXTRACT_PARAMS_SCHEMAS,
    EXTRACT_STYLE_CLASSES,
    Extractor,
)


class ExtractParamsSet(FraguaSet[FraguaParams]):
    """
    Set containing extract parameter schema classes.
    """

    def __init__(self, fg_config: bool, section_name: str = "params") -> None:
        super().__init__(section_name)
        self.fg_config = fg_config
        self._initialize_params()

    def _initialize_params(self) -> None:
        if not self.fg_config:
            return

        for name, params_cls in EXTRACT_PARAMS_SCHEMAS.items():
            instance = params_cls()
            self.add(name, instance)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        return {name: params.summary() for name, params in self.get_all().items()}


class ExtractFunctionSet(FraguaSet[FraguaFunction[FraguaParams]]):
    """
    Set containing extract function classes.
    """

    def __init__(self, fg_config: bool, section_name: str = "functions") -> None:
        super().__init__(section_name)
        self.fg_config = fg_config
        self._initialize_functions()

    def _initialize_functions(self) -> None:
        if not self.fg_config:
            return

        for name, func_cls in EXTRACT_FUNCTION_CLASSES.items():
            instance = func_cls()
            self.add(name, instance)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        return {name: function.summary() for name, function in self.get_all().items()}


class ExtractStyleSet(FraguaSet[FraguaStyle[FraguaParams]]):
    """
    Set containing extract style classes.
    """

    def __init__(self, fg_config: bool, section_name: str = "styles") -> None:
        super().__init__(section_name)
        self.fg_config = fg_config
        self._initialize_styles()

    def _initialize_styles(self) -> None:
        if not self.fg_config:
            return

        for name, style_cls in EXTRACT_STYLE_CLASSES.items():
            instance = style_cls()
            self.add(name, instance)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        return {name: style.summary() for name, style in self.get_all().items()}


class ExtractAgentSet(FraguaSet[Extractor[FraguaParams]]):
    """
    Set containing extract agent instances.
    """

    def __init__(self, section_name: str = "agents") -> None:
        super().__init__(section_name)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        return {name: agent.summary() for name, agent in self.get_all().items()}
