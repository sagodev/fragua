"""
Base TransformParams class.

Defines the common parameter structure for all transform styles.
Each instance encapsulates a DataFrame and style-specific attributes
used by TransformFunction and TransformStyle pipelines.
"""

from typing import Any, Dict, Optional

from pandas import DataFrame

from fragua.core.params import FraguaParams


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

    def summary(self) -> Dict[str, Any]:
        """
        Generate a structured summary of the transform parameters.

        The summary includes:
        - parameter name
        - action type (transform)
        - style identifier
        - field descriptions
        - optional purpose metadata

        Returns:
            Dict[str, Any]:
                Dictionary representation suitable for inspection
                and automated documentation.
        """
        fields: Dict[str, str] = {}

        for name in self.FIELD_DESCRIPTIONS:
            fields[name] = self.FIELD_DESCRIPTIONS.get(
                name, "No description available."
            )

        return {
            "name": self.name,
            "action": self.action,
            "style": self.style,
            "fields": fields,
            "purpose": getattr(self, "purpose", None),
        }
