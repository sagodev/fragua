"""
Base abstract class for all styles in Fragua.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, TypeVar

from fragua.core.fragua_class import FraguaClass
from fragua.core.params import FraguaParams


FraguaParamsT = TypeVar("FraguaParamsT", bound=FraguaParams)


class FraguaStyle(FraguaClass, ABC, Generic[FraguaParamsT]):
    """
    Declarative execution style for Fragua.

    A style defines *how* a function is executed but does not perform
    execution itself. Styles are declarative components and are never
    instantiated directly.
    """

    # Declarative metadata
    action: str
    function: str
    params_type: str
    purpose: str | None = None

    @classmethod
    @abstractmethod
    def execute(cls, params: FraguaParamsT) -> Any:
        """
        Execute the style logic.

        This method is invoked by an Agent at runtime.
        Styles must remain stateless.
        """
        raise NotImplementedError

    @classmethod
    def summary_fields(cls) -> Dict[str, Any]:
        """
        Return a structured summary of the style metadata.
        """
        return {
            "style_name": cls.__name__,
            "purpose": cls.purpose,
            "action": cls.action,
            "function": cls.function,
            "parameters_type": cls.params_type,
        }

    @classmethod
    def summary(cls) -> Dict[str, Any]:
        """
        Generate a declarative summary describing the style.

        Returns:
            A dictionary representing the style summary.
        """
        return {
            "type": "style",
            "name": cls.__name__,
            "fields": cls.summary_fields(),
        }
