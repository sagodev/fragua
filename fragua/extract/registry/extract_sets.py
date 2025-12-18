"""
Extract Sections Module.

Defines the collection sets used to register and organize all extraction-
related components in the Fragua ETL framework, including parameters,
functions, styles, and agents.
"""

from fragua.core.set import FraguaSet


from fragua.extract import (
    EXTRACT_FUNCTION_CLASSES,
    EXTRACT_PARAMS_SCHEMAS,
    EXTRACT_STYLE_CLASSES,
)


class ExtractParamsSet(FraguaSet):
    """
    Set containing extract parameter schema classes.
    """

    def __init__(self, fg_config: bool, section_name: str = "extract_params") -> None:
        super().__init__(section_name, content_kind="class")
        self.fg_config = fg_config
        self._initialize_params()

    def _initialize_params(self) -> None:
        if not self.fg_config:
            return

        for name, params_cls in EXTRACT_PARAMS_SCHEMAS.items():
            self.add(name, params_cls)


class ExtractFunctionSet(FraguaSet):
    """
    Set containing extract function classes.
    """

    def __init__(
        self, fg_config: bool, section_name: str = "extract_functions"
    ) -> None:
        super().__init__(section_name, content_kind="class")
        self.fg_config = fg_config
        self._initialize_functions()

    def _initialize_functions(self) -> None:
        if not self.fg_config:
            return

        for name, func_cls in EXTRACT_FUNCTION_CLASSES.items():
            self.add(name, func_cls)


class ExtractStyleSet(FraguaSet):
    """
    Set containing extract style classes.
    """

    def __init__(self, fg_config: bool, section_name: str = "extract_styles") -> None:
        super().__init__(section_name, content_kind="class")
        self.fg_config = fg_config
        self._initialize_styles()

    def _initialize_styles(self) -> None:
        if not self.fg_config:
            return

        for name, style_cls in EXTRACT_STYLE_CLASSES.items():
            self.add(name, style_cls)


class ExtractAgentSet(FraguaSet):
    """
    Set containing extract agent instances.
    """

    def __init__(self, section_name: str = "extract_agents") -> None:
        super().__init__(section_name, content_kind="instance")
