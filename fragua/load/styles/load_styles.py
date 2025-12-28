"""
Load style specifications for various data loading methods.
"""

from typing import Dict
from fragua.utils.types.enums import ActionType, FieldType, TargetType

LOAD_STYLES: Dict[str, Dict[str, str]] = {
    TargetType.EXCEL.value: {
        FieldType.ACTION.value: ActionType.LOAD.value,
        FieldType.FUNC_KEY.value: TargetType.EXCEL.value,
        FieldType.PURPOSE.value: "Export tabular data to an Excel file.",
    },
    TargetType.CSV.value: {
        FieldType.ACTION.value: ActionType.LOAD.value,
        FieldType.FUNC_KEY.value: TargetType.CSV.value,
        FieldType.PURPOSE.value: "Export tabular data to a CSV file.",
    },
    TargetType.SQL: {
        FieldType.ACTION.value: ActionType.LOAD.value,
        FieldType.FUNC_KEY.value: TargetType.SQL.value,
        FieldType.PURPOSE.value: "Load tabular data into a SQL database.",
    },
    TargetType.API.value: {
        FieldType.ACTION.value: ActionType.LOAD.value,
        FieldType.FUNC_KEY.value: TargetType.API.value,
        FieldType.PURPOSE.value: "Send tabular data to a REST API over HTTP.",
    },
}
