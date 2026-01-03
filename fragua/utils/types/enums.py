"""Enums classes type."""

from enum import Enum


class ComponentType(str, Enum):
    """Fragua components kind class."""

    AGENT = "agent"
    FUNCTION = "function"
    PIPELINE = "pipeline"
    STEP = "step"
    ENVIRONMENT = "environment"
    REGISTRY = "registry"
    SET = "set"
    WAREHOUSE = "warehouse"
    BOX = "box"


class DocumentType(str, Enum):
    """Document types class."""

    DATAFRAME = "dataframe"
    DICT = "dict"
    LIST = "list"
    SCALAR = "scalar"
