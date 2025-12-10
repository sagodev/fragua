"""
Generic LoadFunction class.
"""

from fragua.core.function import FraguaFunction


class LoadFunction(FraguaFunction):
    """
    Generic load function class.
    """

    def __init__(self) -> None:
        super().__init__(function_name=self.__class__.__name__, action="load")
