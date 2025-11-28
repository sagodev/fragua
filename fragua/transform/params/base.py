"""Transform Params Class."""

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
