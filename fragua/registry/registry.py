"""Fragua Instance Registry."""

from fragua.core.registry import FraguaRegistry
from fragua.core.set import FraguaSet
from fragua.sets.extract.functions import EXTRACT_FUNCTIONS
from fragua.sets.load.functions import LOAD_FUNCTIONS
from fragua.sets.load.internal_functions import INTERNAL_LOAD_FUNCTIONS
from fragua.sets.transform.functions import TRANSFORM_FUNCTIONS
from fragua.sets.transform.internal_functions import INTERNAL_TRANSFORM_FUNCTIONS


FRAGUA_SETS = {
    "agents": FraguaSet("agents", components={}),
    "extract_funtions": EXTRACT_FUNCTIONS,
    "transform_functions": TRANSFORM_FUNCTIONS,
    "transform_internal_functions": INTERNAL_TRANSFORM_FUNCTIONS,
    "load_functions": LOAD_FUNCTIONS,
    "load_internal_functions": INTERNAL_LOAD_FUNCTIONS,
}

FRAGUA_REGISTRY = FraguaRegistry("fragua_registry", sets=FRAGUA_SETS)
