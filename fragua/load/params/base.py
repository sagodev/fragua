"""Load Params Class."""

from typing import Any, Dict

from fragua.core.params import Params


class LoadParams(Params):
    """Common parameters for loading agents."""

    def __init__(self, style: str) -> None:
        super().__init__(action="load", style=style)

    def summary(self) -> Dict[str, Any]:
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
