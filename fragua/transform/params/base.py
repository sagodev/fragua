"""
Base TransformParams class.

Defines the common parameter structure for all transform styles.
Each instance encapsulates a DataFrame and style-specific attributes
used by TransformFunction and TransformStyle pipelines.
"""

from typing import Optional

from pandas import DataFrame

from fragua.core.params import FraguaParams

# pylint: disable=too-few-public-methods


class TransformParams(FraguaParams):
    """
    Base class for all transform parameter definitions.

    This class stores the DataFrame to be transformed and provides
    a standardized summary interface for introspection, documentation,
    and UI/CLI rendering.
    """

    def __init__(self, style: str, data: Optional[DataFrame] = None) -> None:
        """
        Initialize transform parameters.

        Args:
            style (str):
                Name of the transform style associated with these parameters.
            data (Optional[DataFrame]):
                Input DataFrame to be transformed. Defaults to an empty DataFrame.
        """
        super().__init__(action="transform", style=style)
        self.data = data if data is not None else DataFrame()
