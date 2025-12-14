"""Extract Params Class."""

from typing import Any, Dict

from fragua.core.params import FraguaParams


class ExtractParams(FraguaParams):
    """
    Base parameter class for all extraction configurations.

    This class provides the common structure and summary behavior
    shared by all extract parameter schemas. Concrete extraction
    parameter classes should extend this class and define their
    specific fields and descriptions.
    """

    def __init__(self, style: str) -> None:
        """
        Initialize extract parameters for a specific extraction style.

        Args:
            style: Identifier of the extraction style (e.g. "csv",
                "excel", "sql", "api").
        """
        super().__init__(action="extract", style=style)

    def summary(self) -> Dict[str, Any]:
        """
        Generate a structured summary of the extract parameters.

        The summary includes the action, style, declared parameter
        fields, and the intended purpose of the parameter set.

        Returns:
            A dictionary containing:
                - name: Parameter class name
                - action: Fixed value "extract"
                - style: Associated extraction style
                - fields: Mapping of parameter names to descriptions
                - purpose: Optional textual description of the params
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
