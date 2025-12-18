"""
Load Sets Module.

Defines the collection sets used to register and organize all loading-
related components in the Fragua ETL framework, including parameters,
functions, styles, and agents.
"""

from fragua.core.set import FraguaSet

from fragua.load import (
    LOAD_FUNCTION_CLASSES,
    LOAD_PARAMS_SCHEMAS,
    LOAD_STYLE_CLASSES,
)


class LoadParamsSet(FraguaSet):
    """
    Set containing load parameter schema classes.
    """

    def __init__(self, fg_config: bool, section_name: str = "load_params") -> None:
        super().__init__(section_name, content_kind="class")
        self.fg_config = fg_config
        self._initialize_params()

    def _initialize_params(self) -> None:
        if not self.fg_config:
            return

        for name, params_cls in LOAD_PARAMS_SCHEMAS.items():
            self.add(name, params_cls)


class LoadFunctionSet(FraguaSet):
    """
    Set containing load function classes.
    """

    def __init__(self, fg_config: bool, section_name: str = "load_functions") -> None:
        super().__init__(section_name, content_kind="class")
        self.fg_config = fg_config
        self._initialize_functions()

    def _initialize_functions(self) -> None:
        if not self.fg_config:
            return

        for name, func_cls in LOAD_FUNCTION_CLASSES.items():
            self.add(name, func_cls)


class LoadStyleSet(FraguaSet):
    """
    Set containing load style classes.
    """

    def __init__(self, fg_config: bool, section_name: str = "load_styles") -> None:
        super().__init__(section_name, content_kind="class")
        self.fg_config = fg_config
        self._initialize_styles()

    def _initialize_styles(self) -> None:
        if not self.fg_config:
            return

        for name, style_cls in LOAD_STYLE_CLASSES.items():
            self.add(name, style_cls)


class LoadAgentSet(FraguaSet):
    """
    Set containing load agent instances.
    """

    def __init__(self, section_name: str = "load_agents") -> None:
        super().__init__(section_name, content_kind="instance")
