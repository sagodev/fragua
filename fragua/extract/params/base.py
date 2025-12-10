"""Extract Params Class."""

from typing import Any, Dict

from fragua.core.params import Params


class ExtractParams(Params):
    """Generic extract params class."""

    def __init__(self, style: str) -> None:
        super().__init__(action="extract", style=style)

    def summary(self) -> Dict[str, Any]:
        """Extract base params class summary."""
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
