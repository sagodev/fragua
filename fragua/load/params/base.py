"""
Base LoadParams class.

Defines the common structure and behavior for all load
parameter objects used in Fragua ETL pipelines.
"""

from typing import Any, Dict

from fragua.core.params import FraguaParams


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

    def summary(self) -> Dict[str, Any]:
        """
        Return a structured summary of the load parameters.

        The summary includes:
        - parameter class name
        - associated action and style
        - declared fields and their descriptions
        - optional functional purpose

        Returns:
            Dict[str, Any]: Serializable summary representation.
        """
        fields = {}

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
