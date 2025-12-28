"""
Extract Styles.

"""

from typing import Dict
from fragua.utils.types.enums import ActionType, FieldType, TargetType


EXTRACT_STYLES: Dict[str, Dict[str, str]] = {
    TargetType.CSV.value: {
        FieldType.ACTION.value: ActionType.EXTRACT.value,
        FieldType.FUNC_KEY.value: TargetType.CSV.value,
        FieldType.PURPOSE.value: "Extract tabular data from CSV files.",
    },
    TargetType.EXCEL.value: {
        FieldType.ACTION.value: ActionType.EXTRACT.value,
        FieldType.FUNC_KEY.value: TargetType.EXCEL.value,
        FieldType.PURPOSE.value: "Extract structured data from Excel spreadsheets.",
    },
    TargetType.SQL.value: {
        FieldType.ACTION.value: ActionType.EXTRACT.value,
        FieldType.FUNC_KEY.value: TargetType.SQL.value,
        FieldType.PURPOSE.value: "Extract records from SQL databases using queries.",
    },
    TargetType.API.value: {
        FieldType.ACTION.value: ActionType.EXTRACT.value,
        FieldType.FUNC_KEY.value: TargetType.API.value,
        FieldType.PURPOSE.value: "Extract data from REST APIs over HTTP.",
    },
}
