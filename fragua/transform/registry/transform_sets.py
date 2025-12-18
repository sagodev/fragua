"""
Transform Sets Module.

Defines the collection sets used to register and organize all transformation-
related components in the Fragua ETL framework, including parameters,
functions, styles, and agents.
"""

from fragua.core.set import FraguaSet

from fragua.transform import (
    TRANSFORM_FUNCTION_CLASSES,
    TRANSFORM_PARAMS_SCHEMAS,
    TRANSFORM_STYLE_CLASSES,
)


class TransformParamsSet(FraguaSet):
    """
    Set containing transform parameter schema classes.
    """

    def __init__(self, fg_config: bool, section_name: str = "transform_params") -> None:
        super().__init__(section_name)
        self.fg_config = fg_config
        self._initialize_params()

    def _initialize_params(self) -> None:
        if not self.fg_config:
            return

        for name, params_cls in TRANSFORM_PARAMS_SCHEMAS.items():
            self.add(name, params_cls)


class TransformFunctionSet(FraguaSet):
    """
    Set containing transform function classes.
    """

    def __init__(
        self, fg_config: bool, section_name: str = "transform_functions"
    ) -> None:
        super().__init__(section_name)
        self.fg_config = fg_config
        self._initialize_functions()

    def _initialize_functions(self) -> None:
        if not self.fg_config:
            return

        for name, func_cls in TRANSFORM_FUNCTION_CLASSES.items():
            self.add(name, func_cls)


class TransformStyleSet(FraguaSet):
    """
    Set containing transform style classes.
    """

    def __init__(self, fg_config: bool, section_name: str = "transform_styles") -> None:
        super().__init__(section_name)
        self.fg_config = fg_config
        self._initialize_styles()

    def _initialize_styles(self) -> None:
        if not self.fg_config:
            return

        for name, style_cls in TRANSFORM_STYLE_CLASSES.items():
            self.add(name, style_cls)


class TransformAgentSet(FraguaSet):
    """
    Set containing transform agent instances.
    """

    def __init__(self, section_name: str = "transform_agents") -> None:
        super().__init__(section_name)
