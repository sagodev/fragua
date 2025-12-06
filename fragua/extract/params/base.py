"""Extract Params Class."""

from typing import Any, Dict

from fragua.core.params import Params


class ExtractParams(Params):
    """Common parameters for extraction agents."""

    read_kwargs: Dict[str, Any]

    purpose: str | None = (
        "Base extraction parameters used across all extract-style agents."
    )

    FIELD_DESCRIPTIONS = {
        "read_kwargs": "Additional keyword arguments passed to the data reader.",
    }

    def __init__(self, style: str, read_kwargs: Dict[str, Any] | None = None) -> None:
        super().__init__(action="extract", style=style)
        self.read_kwargs = read_kwargs or {}

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
