"""Transform Registry."""

from fragua.core.registry import FraguaRegistry
from fragua.core.set import FraguaSet
from fragua.sets.transform.functions import TRANSFORM_FUNCTIONS
from fragua.sets.transform.internal_functions import TRANSFORM_INTERNAL_FUNCTIONS
from fragua.utils.types.enums import ComponentType

TRANSFORM_SETS = {
    ComponentType.FUNCTION.value: TRANSFORM_FUNCTIONS,
    ComponentType.INTERNAL_FUNCTION.value: TRANSFORM_INTERNAL_FUNCTIONS,
    ComponentType.AGENT.value: FraguaSet("transform_agents", components={}),
}

TRANSFORM_REGISTRY = FraguaRegistry("transform_registry", TRANSFORM_SETS)
