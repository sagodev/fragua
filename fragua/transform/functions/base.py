"""
Generic TransformFunction class.
"""

from fragua.core.function import FraguaFunction


class TransformFunction(FraguaFunction):
    """
    Base class for all transformation functions in Fragua.

    A TransformFunction encapsulates a single, reusable transformation
    operation that can be invoked by a TransformStyle as part of a
    transformation pipeline.
    """

    def __init__(self) -> None:
        """
        Initialize the transformation function.

        The function name is automatically inferred from the class name,
        and the associated action is fixed to 'transform'.
        """
        super().__init__(function_name=self.__class__.__name__, action="transform")
