"""
Extract Styles.

"""

from typing import Any, Dict
from fragua.extract.params.extract_params import (
    APIExtractParams,
    CSVExtractParams,
    ExcelExtractParams,
    SQLExtractParams,
)


EXTRACT_STYLES: Dict[str, Dict[str, Any]] = {
    "csv": {
        "action": "extract",
        "function": "csv",
        "params_type": CSVExtractParams,
        "purpose": "Extract tabular data from CSV files.",
    },
    "excel": {
        "action": "extract",
        "function": "excel",
        "params_type": ExcelExtractParams,
        "purpose": "Extract structured data from Excel spreadsheets.",
    },
    "sql": {
        "action": "extract",
        "function": "sql",
        "params_type": SQLExtractParams,
        "purpose": "Extract records from SQL databases using queries.",
    },
    "api": {
        "action": "extract",
        "function": "api",
        "params_type": APIExtractParams,
        "purpose": "Extract data from REST APIs over HTTP.",
    },
}
