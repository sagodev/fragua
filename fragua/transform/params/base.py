"""Transform Params Class."""

from typing import Any, Dict
from pandas import DataFrame

from fragua.core.params import Params


class TransformParams(Params):
    """Common parameters for transformation agents."""

    data: DataFrame

    purpose: str | None = "Base parameters for all data transformation operations."

    FIELD_DESCRIPTIONS = {
        "data": "Input DataFrame that will be transformed.",
    }

    def __init__(self, style: str, data: DataFrame) -> None:
        super().__init__(action="transform", style=style)
        self.data = data

    def summary(self) -> Dict[str, Any]:
        fields = {}

        for name in self.__annotations__:
            desc = self.FIELD_DESCRIPTIONS.get(name, "No description available.")
            fields[name] = desc

        return {
            "name": self.__class__.__name__,
            "action": self.action,
            "style": self.style,
            "fields": fields,
            "purpose": getattr(self, "purpose", None),
        }
