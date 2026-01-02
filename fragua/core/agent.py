"""Fragua agent.

Defines the minimal execution primitive responsible for
running ETL functions.
"""

from typing import Any, Callable


class FraguaAgent:
    """
    Stateless execution agent.

    A FraguaAgent executes callables and returns their results.
    It does not resolve functions, store data or manage metadata.
    """

    def __init__(self, name: str) -> None:
        """
        Initialize the agent.

        Parameters
        ----------
        name:
            Logical name of the agent.
        """
        self.name = name

    def execute(self, fn: Callable[..., Any], **kwargs: Any) -> Any:
        """
        Execute a callable with the provided arguments.

        Parameters
        ----------
        fn:
            Callable ETL function to execute.
        kwargs:
            Keyword arguments passed to the callable.

        Returns
        -------
        Any
            The result produced by the callable.
        """
        if not callable(fn):
            raise TypeError("fn must be a callable")

        return fn(**kwargs)
