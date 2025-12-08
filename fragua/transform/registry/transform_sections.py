"""Transform Sections Module."""

from typing import Any, Dict, cast
import pandas as pd
from fragua.core.section_registry import SectionRegistry
from fragua.transform import (
    TRANSFORM_FUNCTION_CLASSES,
    TRANSFORM_PARAMS_CLASSES,
    TRANSFORM_STYLE_CLASSES,
    TransformStyle,
    TransformFunction,
    TransformParams,
    Transformer,
)


class TransformParamsSection(SectionRegistry):
    """Section containing transform parameters classes."""

    def __init__(self, section_name: str = "params") -> None:
        super().__init__(section_name)
        self._initialize_params()

    def _initialize_params(self) -> None:
        """Transform all predefined transform parameter classes into the section."""
        for name, cls in TRANSFORM_PARAMS_CLASSES.items():
            self.create_entry(name, cls)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Return a structured summary of all Transform parameter classes.
        """
        result: Dict[str, Dict[str, Any]] = {}

        for name, cls in self.get_entries().items():
            obj = cls.__new__(cls)
            obj = cast(TransformParams, obj)
            df = pd.DataFrame({})
            TransformParams.__init__(obj, style=name, data=df)

            data = obj.summary()

            result[name] = data

        return result


class TransformFunctionSection(SectionRegistry):
    """Transform functions section."""

    def __init__(self, section_name: str = "functions") -> None:
        super().__init__(section_name)
        self._initialize_functions()

    def _initialize_functions(self) -> None:
        """Transform all predefined Transform functions into the section."""
        for name, cls in TRANSFORM_FUNCTION_CLASSES.items():
            self.create_entry(name, cls)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Return a structured summary of all Transform functions.
        """
        result: Dict[str, Dict[str, Any]] = {}

        for name, cls in self.get_entries().items():
            df = pd.DataFrame({})

            params = TransformParams.__new__(TransformParams)
            TransformParams.__init__(params, style=name, data=df)

            obj = cls.__new__(cls)
            obj = cast(TransformFunction, obj)
            obj.name = name
            obj.params = params

            data = obj.summary()

            result[name] = data

        return result


class TransformStyleSection(SectionRegistry):
    """Section that stores all Transform style classes."""

    def __init__(self, section_name: str = "styles") -> None:
        super().__init__(section_name)
        self._initialize_styles()

    def _initialize_styles(self) -> None:
        """Transform predefined Transform style classes into the section."""
        for name, cls in TRANSFORM_STYLE_CLASSES.items():
            self.create_entry(name, cls)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Summary of all Transform style classes.
        """
        result: Dict[str, Dict[str, Any]] = {}

        for name, cls in self.get_entries().items():

            obj = cls.__new__(cls)
            obj = cast(TransformStyle, obj)
            data = obj.summary()

            result[name] = data

        return result


class TransformAgentSection(SectionRegistry):
    """Transform agents section."""

    def __init__(self, section_name="agents"):
        super().__init__(section_name)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """Transform agents section summary."""
        result: Dict[str, Dict[str, Any]] = {}

        for name, cls in self.get_entries().items():

            obj = cls.__new__(cls)
            obj = cast(Transformer, obj)
            data = obj.summary()

            result[name] = data

        return result
