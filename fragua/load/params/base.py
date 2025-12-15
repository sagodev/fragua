"""
Base LoadParams class.

Defines the common structure and behavior for all load
parameter objects used in Fragua ETL pipelines.
"""

from fragua.core.params import FraguaParams

# pylint: disable=too-few-public-methods


class LoadParams(FraguaParams):
    """
    Base class for load parameters.

    LoadParams objects encapsulate all configuration values required
    by a load style and its underlying function to persist data
    into an external destination.
    """

    def __init__(self, style: str) -> None:
        """
        Initialize load parameters.

        Args:
            style (str):
                Load style identifier associated with this parameter set.
        """
        super().__init__(action="load", style=style)
