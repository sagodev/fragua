"""Extract result DataFrame from an Fraguabox and create a document of an given type."""

from typing import Any
import pandas as pd

from fragua.utils.types.enums import DocumentType


def from_box_to_doc(
    box: dict[str, Any],
    *,
    key: str,
    doc_type: DocumentType,
) -> Any:
    """
    Extract a result from a FraguaBox entry, validating its document type.

    Args:
        box (dict[str, Any]):
            FraguaBox (warehouse entry) containing execution results.
        key (str):
            Logical key under which the result is stored.
        doc_type (DocumentType):
            Expected document type of the result.

    Returns:
        Any:
            The extracted result if it matches the expected type.

    Raises:
        KeyError:
            If the key does not exist in the box.
        TypeError:
            If the result does not match the expected document type.
    """
    if key not in box:
        raise KeyError(f"Result key '{key}' not found in FraguaBox.")

    result = box[key]

    if doc_type is DocumentType.DATAFRAME:
        if not isinstance(result, pd.DataFrame):
            raise TypeError(
                f"Expected pandas.DataFrame for key '{key}', "
                f"got {type(result).__name__}."
            )
        return result

    if doc_type is DocumentType.DICT:
        if not isinstance(result, dict):
            raise TypeError(
                f"Expected dict for key '{key}', got {type(result).__name__}."
            )
        return result

    if doc_type is DocumentType.LIST:
        if not isinstance(result, list):
            raise TypeError(
                f"Expected list for key '{key}', got {type(result).__name__}."
            )
        return result

    if doc_type is DocumentType.SCALAR:
        if isinstance(result, (dict, list, pd.DataFrame)):
            raise TypeError(
                f"Expected scalar value for key '{key}', "
                f"got {type(result).__name__}."
            )
        return result

    raise ValueError(f"Unsupported DocumentType: {doc_type}")
