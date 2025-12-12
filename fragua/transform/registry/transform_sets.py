"""Transform Sets Module."""

from typing import Any, Dict, cast
from fragua.core.set import FraguaSet
from fragua.transform import (
    TRANSFORM_FUNCTION_CLASSES,
    TRANSFORM_PARAMS_CLASSES,
    TRANSFORM_STYLE_CLASSES,
    TransformStyle,
    TransformFunction,
    TransformParams,
    Transformer,
)


class TransformParamsSet(FraguaSet):
    """Set containing transform parameters classes."""

    def __init__(self, fg_config: bool, set_name: str = "params") -> None:
        super().__init__(set_name)
        self._initialize_params()
        self.fg_config = fg_config

    def _initialize_params(self) -> None:
        """Transform all predefined transform parameter classes into the set."""
        if self.fg_config:
            for name, cls in TRANSFORM_PARAMS_CLASSES.items():
                cls = cast(TransformParams, cls)
                self.add(name, cls)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Return a structured summary of all Transform parameter classes.
        """
        result: Dict[str, Dict[str, Any]] = {}

        if self.fg_config:
            for name, cls in self.get_all().items():
                obj = cast(TransformParams, cls)
                TransformParams.__init__(obj, style=name)
                data = obj.summary()
                result[name] = data

        return result


class TransformFunctionSet(FraguaSet):
    """Transform functions set."""

    def __init__(self, fg_config: bool, set_name: str = "functions") -> None:
        super().__init__(set_name)
        self.fg_config = fg_config
        self._initialize_functions()

    def _initialize_functions(self) -> None:
        """Transform all predefined Transform functions into the set."""
        if self.fg_config:
            for name, cls in TRANSFORM_FUNCTION_CLASSES.items():
                cls = cast(TransformFunction, cls)
                self.add(name, cls)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Return a structured summary of all Transform functions.
        """
        result: Dict[str, Dict[str, Any]] = {}

        if self.fg_config:
            for name, cls in self.get_all().items():
                obj = cast(TransformFunction, cls)
                obj.name = name
                data = obj.summary()
                result[name] = data

        return result


class TransformStyleSet(FraguaSet):
    """Set that stores all Transform style classes."""

    def __init__(self, fg_config: bool, set_name: str = "styles") -> None:
        super().__init__(set_name)
        self.fg_config = fg_config
        self._initialize_styles()

    def _initialize_styles(self) -> None:
        """Transform predefined Transform style classes into the set."""
        if self.fg_config:
            for name, cls in TRANSFORM_STYLE_CLASSES.items():
                cls = cast(TransformStyle, cls)
                self.add(name, cls)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Summary of all Transform style classes.
        """
        result: Dict[str, Dict[str, Any]] = {}

        if self.fg_config:
            for name, cls in self.get_all().items():
                obj = cast(TransformStyle, cls)
                data = obj.summary()
                result[name] = data

        return result


class TransformAgentSet(FraguaSet):
    """Transform agents set."""

    def __init__(self, set_name="agents"):
        super().__init__(set_name)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """Transform agents set summary."""
        result: Dict[str, Dict[str, Any]] = {}

        for name, instance in self.get_all().items():
            obj = cast(Transformer, instance)
            data = obj.summary()
            result[name] = data

        return result
