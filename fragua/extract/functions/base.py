"""
Generic ExtractFunction class.
"""

from fragua.core.function import FraguaFunction


class ExtractFunction(FraguaFunction):
    """
    Base class for all extraction-related functions in Fragua.

    This class provides a concrete specialization of FraguaFunction
    for the "extract" action. It does not implement execution logic
    itself and is intended to be subclassed by concrete extract
    functions that define specific extraction behavior.
    """

    def __init__(self) -> None:
        """
        Initialize the extract function.

        The function name is automatically derived from the concrete
        subclass name and the action is fixed to "extract".
        """
        super().__init__(function_name=self.__class__.__name__, action="extract")
