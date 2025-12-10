"""
Generic ExtractFunction class.
"""

from abc import abstractmethod
from typing import Any, Dict

from fragua.core.function import FraguaFunction


class ExtractFunction(FraguaFunction):
    """
    Generic extract function class.
    """

    def __init__(self) -> None:
        super().__init__(function_name=self.__class__.__name__, action="extract")

    @abstractmethod
    def summary(self) -> Dict[str, Any]:
        """Base extract function summary."""
