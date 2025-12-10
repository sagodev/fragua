"""Transform Params Class."""

from typing import Any, Dict, Optional

from pandas import DataFrame

from fragua.core.params import Params


class TransformParams(Params):
    """Common parameters for transformation agents."""

    def __init__(self, style: str, data: Optional[DataFrame] = None) -> None:
        super().__init__(action="transform", style=style)
        self.data = data if data is not None else DataFrame()

    def summary(self) -> Dict[str, Any]:
        fields = {}

        for name in self.__annotations__:
            desc = self.FIELD_DESCRIPTIONS.get(name, "No description available.")
            fields[name] = desc

        return {
            "name": self.name,
            "action": self.action,
            "style": self.style,
            "fields": fields,
            "purpose": getattr(self, "purpose", None),
        }
