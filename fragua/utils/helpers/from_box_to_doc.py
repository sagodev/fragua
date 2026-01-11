"""Extract result object from a FraguaBox and create a document of a given type."""

from typing import Any
import io

from fragua.utils.types.enums import DocumentType


def from_box_to_doc(
    box: dict[str, Any],
    *,
    key: str,
    doc_type: DocumentType,
) -> Any:
    """
    Extract a tabular-like result object from a FraguaBox and serialize it
    into the requested document type.

    The stored object is expected to follow a DataFrame-like interface
    (duck typing), providing the required serialization methods:
        - to_csv()
        - to_json()
        - to_excel()

    Args:
        box:
            FraguaBox result mapping.
        key:
            Key under which the result object is stored.
        doc_type:
            Desired output document type.

    Returns:
        Serialized document representation.

    Raises:
        KeyError:
            If the key does not exist in the box.
        ValueError:
            If the document type is unsupported.
        AttributeError:
            If the result object does not provide the required methods.
    """
    if key not in box:
        raise KeyError(f"Result key '{key}' not found in FraguaBox.")

    result = box[key]

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
