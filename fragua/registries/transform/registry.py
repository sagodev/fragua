"""Transform Registry."""

from fragua.core.registry import FraguaRegistry
from fragua.sets.transform.functions import TRANSFORM_FUNCTIONS
from fragua.utils.types.enums import ComponentType

TRANSFORM_SETS = {
    ComponentType.FUNCTION.value: TRANSFORM_FUNCTIONS,
    ComponentType.AGENT.value: {},
}

TRANSFORM_REGISTRY = FraguaRegistry("transform_registry", TRANSFORM_SETS)
