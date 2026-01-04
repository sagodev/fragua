"""Extract result DataFrame from a FraguaBox and create a document of a given type."""

from typing import Any
import io
import pandas as pd

from fragua.utils.types.enums import DocumentType


def from_box_to_doc(
    box: dict[str, Any],
    *,
    key: str,
    doc_type: DocumentType,
) -> Any:
    """
    Extract a DataFrame result from a FraguaBox and serialize it
    into the requested document type.

    Args:
        box:
            FraguaBox result mapping.
        key:
            Key under which the DataFrame is stored.
        doc_type:
            Desired output document type.

    Returns:
        Serialized document representation.

    Raises:
        KeyError:
            If the key does not exist in the box.
        TypeError:
            If the stored result is not a DataFrame.
        ValueError:
            If the document type is unsupported.
    """
    if key not in box:
        raise KeyError(f"Result key '{key}' not found in FraguaBox.")

    result = box[key]

    if not isinstance(result, pd.DataFrame):
        raise TypeError(
            f"Expected pandas.DataFrame for key '{key}', "
            f"got {type(result).__name__}."
        )

    if doc_type is DocumentType.DATAFRAME:
        return result

    if doc_type is DocumentType.CSV:
        return result.to_csv(index=False)

    if doc_type is DocumentType.JSON:
        return result.to_json(orient="records")

    if doc_type is DocumentType.EXCEL:
        buffer = io.BytesIO()
        result.to_excel(buffer, index=False)
        buffer.seek(0)
        return buffer.getvalue()

    raise ValueError(f"Unsupported DocumentType: {doc_type}")
