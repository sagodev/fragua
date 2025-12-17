"""
Base abstract class for all function schemas used by styles in Fragua.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, Iterable, Optional, Type, TypeVar

from fragua.core.component import FraguaComponent
from fragua.core.params import FraguaParamsT


class FraguaFunction(FraguaComponent, ABC, Generic[FraguaParamsT]):
    """
    Abstract base class for all executable functions in Fragua.

    A FraguaFunction represents a stateless, reusable unit of logic
    executed as part of an ETL workflow.
    """

    action: str
    params_type: Type[FraguaParamsT]
    purpose: str | None = None
    steps: Iterable[str] | None = None

    def __init__(self, function_name: Optional[str] = None) -> None:
        super().__init__(component_name=function_name or self.__class__.__name__)

    @abstractmethod
    def execute(
        self,
        input_data: Any,
        params: FraguaParamsT,
        context: Any,
    ) -> Any:
        """
        Execute the function logic.

        Args:
            input_data:
                Input payload. None for extract, DataFrame for transform/load.
            params:
                Parameters instance defining execution behavior.
            context:
                Runtime execution context.

        Returns:
            Execution result.
        """
        raise NotImplementedError

    def summary(self) -> Dict[str, Any]:
        """
        Return a structured summary of the function.
        """
        summary: Dict[str, Any] = {
            "name": self.name,
            "action": self.action,
            "purpose": self.purpose,
            "params": self.params_type().summary(),
        }

        if self.steps:
            summary["steps"] = self.steps

        return summary


FraguaFunctionT = TypeVar("FraguaFunctionT", bound=FraguaFunction)
