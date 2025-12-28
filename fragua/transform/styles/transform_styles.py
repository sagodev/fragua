"""
Transform style specifications for different data transformation scenarios.
"""

from typing import Dict
from fragua.utils.types.enums import ActionType, FieldType, TargetType

TRANSFORM_STYLES: Dict[str, Dict[str, str]] = {
    TargetType.ML.value: {
        FieldType.ACTION.value: ActionType.TRANSFORM.value,
        FieldType.FUNC_KEY.value: TargetType.ML.value,
        FieldType.PURPOSE.value: "Apply machine learning preprocessing steps.",
    },
    TargetType.REPORT.value: {
        FieldType.ACTION.value: ActionType.TRANSFORM.value,
        FieldType.FUNC_KEY.value: TargetType.REPORT.value,
        FieldType.PURPOSE.value: "Prepare data for reporting.",
    },
    TargetType.ANALYSIS.value: {
        FieldType.ACTION.value: ActionType.TRANSFORM.value,
        FieldType.FUNC_KEY.value: TargetType.ANALYSIS.value,
        FieldType.PURPOSE.value: "Perform analytical transformations.",
    },
}
