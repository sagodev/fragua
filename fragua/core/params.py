"""
Base class for declarative parameter schemas in Fragua.
"""

from typing import Any, Dict, Optional, TypeVar
from fragua.core.component import FraguaComponent
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


class FraguaParams(FraguaComponent):
    """
    Declarative parameter schema for Fragua components.

    A FraguaParams defines the configuration contract required by
    functions or styles during ETL execution. It is action-agnostic
    and style-agnostic, focusing exclusively on parameter structure,
    validation, and introspection.
    """

    purpose: Optional[str] = None

    FIELDS: Dict[str, Dict[str, Any]] = {}

    def __init__(self, **values: Any) -> None:
        super().__init__(component_name=self.__class__.__name__)
        self._values: Dict[str, Any] = {}
        self._load(values)

    def _load(self, values: Dict[str, Any]) -> None:
        for field_name, spec in self.FIELDS.items():
            if field_name in values:
                value = values[field_name]
            elif spec.get("required", False):
                raise ValueError(f"Missing required parameter: {field_name}")
            else:
                value = spec.get("default")

            normalizer = spec.get("normalize")
            if normalizer and value is not None:
                try:
                    value = normalizer(value)
                except Exception as exc:  # pylint: disable=broad-except
                    logger.error(
                        "Failed to normalize param '%s': %s",
                        field_name,
                        exc,
                    )
                    raise

            self._values[field_name] = value

    def get(self, name: str) -> Any:
        """Return the value of a parameter."""
        return self._values.get(name)

    def summary(self) -> Dict[str, Any]:
        """
        Return a structured summary of the params schema.

        Returns:
            Dict[str, Any]: Serializable summary representation.
        """
        fields: Dict[str, Dict[str, Any]] = {}

        for name, spec in self.FIELDS.items():
            field_type = spec.get("type")

            fields[name] = {
                "description": spec.get("description", "No description available."),
                "required": spec.get("required", False),
                "default": spec.get("default"),
                "type": (
                    field_type.__name__
                    if field_type and hasattr(field_type, "__name__")
                    else None
                ),
            }

        return {
            "name": self.name,
            "purpose": self.purpose,
            "fields": fields,
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._values})"


FraguaParamsT = TypeVar("FraguaParamsT", bound=FraguaParams)
