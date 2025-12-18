"""
Base abstract class for all executable functions in Fragua.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, Iterable, Type, TypeVar

from fragua.core.fragua_class import FraguaClass
from fragua.core.params import FraguaParams


FraguaParamsT = TypeVar("FraguaParamsT", bound=FraguaParams)


class FraguaFunction(FraguaClass, ABC, Generic[FraguaParamsT]):
    """
    Declarative processing function for Fragua.

    A FraguaFunction defines *what* operation is performed during an
    ETL workflow. Functions are stateless and declarative.
    """

    action: str
    params_type: Type[FraguaParamsT]
    purpose: str | None = None
    steps: Iterable[str] | None = None

    @classmethod
    @abstractmethod
    def execute(
        cls,
        input_data: Any,
        params: FraguaParamsT,
        context: Any,
    ) -> Any:
        """
        Execute the function logic.

        Execution is coordinated by an Agent.
        Functions must remain stateless.
        """
        raise NotImplementedError

    @classmethod
    def summary(cls) -> Dict[str, Any]:
        """
        Return a declarative summary of the function.
        """
        summary: Dict[str, Any] = {
            "type": "function",
            "name": cls.__name__,
            "action": cls.action,
            "purpose": cls.purpose,
            "params": cls.params_type.summary(),
        }

        if cls.steps:
            summary["steps"] = list(cls.steps)

        return summary


FraguaFunctionT = TypeVar("FraguaFunctionT", bound=FraguaFunction)
