"""
Generic ExtractFunction class.
"""

from abc import abstractmethod
from typing import Any, Dict, Generic

from fragua.core.function import FraguaFunction
from fragua.extract.params import ExtractParamsT


class ExtractFunction(FraguaFunction[ExtractParamsT], Generic[ExtractParamsT]):
    """
    Generic ExtractFunction for Fragua, typed by the specific ExtractParams subclass.
    """

    def __init__(self, name: str, params: ExtractParamsT) -> None:
        super().__init__(function_name=name, action="extract", params=params)

    @abstractmethod
    def summary(self) -> Dict[str, Any]:
        """Base extract function summary."""
