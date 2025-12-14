"""Transform Params Class."""

from typing import Any, Dict, Optional

from pandas import DataFrame

from fragua.core.params import FraguaParams


class TransformParams(FraguaParams):
    """Base transform params class."""

    def __init__(self, style: str, data: Optional[DataFrame] = None) -> None:
        super().__init__(action="transform", style=style)
        self.data = data if data is not None else DataFrame()

    def summary(self) -> Dict[str, Any]:
        """Transform params class summary."""
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
