"""Extract registry."""

from fragua.core.registry import FraguaRegistry
from fragua.sets.extract.functions import EXTRACT_FUNCTIONS
from fragua.utils.types.enums import ComponentType

EXTRACT_SETS = {
    ComponentType.FUNCTION.value: EXTRACT_FUNCTIONS,
    ComponentType.AGENT.value: {},
}

EXTRACT_REGISTRY = FraguaRegistry("extract_registry", EXTRACT_SETS)
