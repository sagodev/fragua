"""
Generic TransformFunction class.
"""

from fragua.core.function import FraguaFunction
from fragua.transform.params.base import TransformParams


class TransformFunction(FraguaFunction):
    """
    Generic transform function class.
    """

    def __init__(self) -> None:
        super().__init__(function_name=self.__class__.__name__, action="transform")
