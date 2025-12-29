"""Load registry."""

from fragua.core.registry import FraguaRegistry
from fragua.core.set import FraguaSet
from fragua.sets.load.functions import LOAD_FUNCTIONS
from fragua.utils.types.enums import ComponentType

LOAD_SETS = {
    ComponentType.FUNCTION.value: LOAD_FUNCTIONS,
    ComponentType.AGENT.value: FraguaSet("load_agents", components={}),
}

LOAD_REGISTRY = FraguaRegistry("load_registry", LOAD_SETS)
