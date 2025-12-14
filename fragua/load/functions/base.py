"""
Generic LoadFunction class.

Defines the base class for all load functions in Fragua.
Load functions are responsible for persisting data into
target destinations (files, databases, external systems).
"""

from fragua.core.function import FraguaFunction


class LoadFunction(FraguaFunction):
    """
    Base class for all load functions.

    A LoadFunction:
    - belongs to the "load" action
    - receives already processed data via LoadParams
    - performs the final persistence step of the pipeline
    """

    def __init__(self) -> None:
        """Initialize the load function with the 'load' action."""
        super().__init__(
            function_name=self.__class__.__name__,
            action="load",
        )
