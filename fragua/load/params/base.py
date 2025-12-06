"""Load Params Class."""

from typing import Any, Dict
from pandas import DataFrame

from fragua.core.params import Params


class LoadParams(Params):
    """Common parameters for loading agents."""

    data: DataFrame
    destination: str | None

    FIELD_DESCRIPTIONS = {
        "data": "Pandas DataFrame containing the data to be loaded.",
        "destination": "Optional destination identifier (e.g., file path, database name, endpoint)",
    }

    def __init__(
        self, style: str, data: DataFrame, destination: str | None = None
    ) -> None:
        super().__init__(action="load", style=style)
        self.data = data
        self.destination = destination

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
