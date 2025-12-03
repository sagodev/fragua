"""Load Functions."""

from typing import Any, Dict, Type
import pandas as pd


from fragua.load.functions.base import LoadFunction
from fragua.load.functions.internal_functions import (
    build_excel_path,
    convert_datetime_columns,
    validate_excel_params,
    write_excel,
)
from fragua.load.params.base import LoadParams
from fragua.load.params.generic_types import ExcelLoadParamsT


class ExcelLoadFunction(LoadFunction[ExcelLoadParamsT]):
    """
    LoadFunction for Excel pipelines.
    """

    PURPOSE: str = "Export a DataFrame to an Excel file."

    def __init__(self, name: str, params: ExcelLoadParamsT) -> None:
        super().__init__(name=name, params=params)

    def execute(self) -> pd.DataFrame:
        validate_excel_params(self.params)
        path = build_excel_path(self.params)
        df = convert_datetime_columns(self.params.data)
        write_excel(df, path, self.params.sheet_name or "Sheet1", self.params.index)
        return df

    def summary(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "params_type": type(self.params).__name__,
            "purpose": self.PURPOSE,
        }


LOAD_FUNCTION_CLASSES: Dict[str, Type[LoadFunction[LoadParams]]] = {
    "excel": ExcelLoadFunction,
}
