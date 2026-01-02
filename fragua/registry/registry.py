"""Fragua Instance Registry."""

from typing import Any, Dict

from fragua_sets import (
    PIPELINE_EXTRACT_FUNCTIONS,
    PIPELINE_LOAD_FUNCTIONS,
    PIPELINE_TRANSFORM_FUNCTIONS,
    INTERNAL_LOAD_FUNCTIONS,
    INTERNAL_TRANSFORM_FUNCTIONS,
)

from fragua.core.registry import FraguaRegistry
from fragua.core.set import FraguaSet


FRAGUA_SETS: Dict[str, FraguaSet[Any]] = {
    "agent": FraguaSet("agent", components={}),
    "extract_functions": PIPELINE_EXTRACT_FUNCTIONS,
    "transform_functions": PIPELINE_TRANSFORM_FUNCTIONS,
    "internal_transform_functions": INTERNAL_TRANSFORM_FUNCTIONS,
    "load_functions": PIPELINE_LOAD_FUNCTIONS,
    "internal_load_functions": INTERNAL_LOAD_FUNCTIONS,
}

FRAGUA_REGISTRY = FraguaRegistry("fragua_registry", sets=FRAGUA_SETS)
