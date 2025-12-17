"""
Load Sets Module.

Defines the collection sets used to register and organize all loading-
related components in the Fragua ETL framework, including parameters,
functions, styles, and agents.
"""

from typing import Any, Dict

from fragua.core.function import FraguaFunction
from fragua.core.params import FraguaParams
from fragua.core.set import FraguaSet
from fragua.core.style import FraguaStyle

from fragua.load import (
    LOAD_FUNCTION_CLASSES,
    LOAD_PARAMS_SCHEMAS,
    LOAD_STYLE_CLASSES,
    Loader,
)


class LoadParamsSet(FraguaSet[FraguaParams]):
    """
    Set containing load parameter schema classes.
    """

    def __init__(self, fg_config: bool, section_name: str = "params") -> None:
        super().__init__(section_name)
        self.fg_config = fg_config
        self._initialize_params()

    def _initialize_params(self) -> None:
        if not self.fg_config:
            return

        for name, params_cls in LOAD_PARAMS_SCHEMAS.items():
            instance = params_cls()
            self.add(name, instance)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        return {name: params.summary() for name, params in self.get_all().items()}


class LoadFunctionSet(FraguaSet[FraguaFunction[FraguaParams]]):
    """
    Set containing load function classes.
    """

    def __init__(self, fg_config: bool, section_name: str = "functions") -> None:
        super().__init__(section_name)
        self.fg_config = fg_config
        self._initialize_functions()

    def _initialize_functions(self) -> None:
        if not self.fg_config:
            return

        for name, func_cls in LOAD_FUNCTION_CLASSES.items():
            instance = func_cls()
            self.add(name, instance)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        return {name: function.summary() for name, function in self.get_all().items()}


class LoadStyleSet(FraguaSet[FraguaStyle[FraguaParams]]):
    """
    Set containing load style classes.
    """

    def __init__(self, fg_config: bool, section_name: str = "styles") -> None:
        super().__init__(section_name)
        self.fg_config = fg_config
        self._initialize_styles()

    def _initialize_styles(self) -> None:
        if not self.fg_config:
            return

        for name, style_cls in LOAD_STYLE_CLASSES.items():
            instance = style_cls()
            self.add(name, instance)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        return {name: style.summary() for name, style in self.get_all().items()}


class LoadAgentSet(FraguaSet[Loader[FraguaParams]]):
    """
    Set containing load agent instances.
    """

    def __init__(self, section_name: str = "agents") -> None:
        super().__init__(section_name)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        return {name: agent.summary() for name, agent in self.get_all().items()}
