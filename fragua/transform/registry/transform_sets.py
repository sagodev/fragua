"""Transform Sets Module."""

from typing import Any, Dict, cast
from fragua.core.registry_set import RegistrySet
from fragua.transform import (
    TRANSFORM_FUNCTION_CLASSES,
    TRANSFORM_PARAMS_CLASSES,
    TRANSFORM_STYLE_CLASSES,
    TransformStyle,
    TransformFunction,
    TransformParams,
    Transformer,
)


class TransformParamsSet(RegistrySet):
    """Set containing transform parameters classes."""

    def __init__(self, set_name: str = "params") -> None:
        super().__init__(set_name)
        self._initialize_params()

    def _initialize_params(self) -> None:
        """Transform all predefined transform parameter classes into the set."""
        for name, cls in TRANSFORM_PARAMS_CLASSES.items():
            self.create_one(name, cls)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Return a structured summary of all Transform parameter classes.
        """
        result: Dict[str, Dict[str, Any]] = {}

        for name, cls in self.get_all().items():
            obj = cls.__new__(cls)
            obj = cast(TransformParams, obj)
            TransformParams.__init__(obj, style=name)

            data = obj.summary()

            result[name] = data

        return result


class TransformFunctionSet(RegistrySet):
    """Transform functions set."""

    def __init__(self, set_name: str = "functions") -> None:
        super().__init__(set_name)
        self._initialize_functions()

    def _initialize_functions(self) -> None:
        """Transform all predefined Transform functions into the set."""
        for name, cls in TRANSFORM_FUNCTION_CLASSES.items():
            self.create_one(name, cls)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Return a structured summary of all Transform functions.
        """
        result: Dict[str, Dict[str, Any]] = {}

        for name, cls in self.get_all().items():

            params = TransformParams.__new__(TransformParams)
            TransformParams.__init__(params, style=name)

            obj = cls.__new__(cls)
            obj = cast(TransformFunction, obj)
            obj.name = name
            obj.params = params

            data = obj.summary()

            result[name] = data

        return result


class TransformStyleSet(RegistrySet):
    """Set that stores all Transform style classes."""

    def __init__(self, set_name: str = "styles") -> None:
        super().__init__(set_name)
        self._initialize_styles()

    def _initialize_styles(self) -> None:
        """Transform predefined Transform style classes into the set."""
        for name, cls in TRANSFORM_STYLE_CLASSES.items():
            self.create_one(name, cls)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Summary of all Transform style classes.
        """
        result: Dict[str, Dict[str, Any]] = {}

        for name, cls in self.get_all().items():

            obj = cls.__new__(cls)
            obj = cast(TransformStyle, obj)
            data = obj.summary()

            result[name] = data

        return result


class TransformAgentSet(RegistrySet):
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
