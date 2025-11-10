"""
Reusable Functions Module.
"""

from fragua.functions.function import (
    FUNCTIONS_REGISTRY,
    register_function,
    get_function,
    list_functions,
    FraguaFunction,
)

# Import modules to auto-register their functions
from fragua.functions import (
    extract_functions,
    load_functions,
    transform_functions,
)  # noqa: F401


__all__ = [
    # Registry Functions
    "FUNCTIONS_REGISTRY",
    "register_function",
    "get_function",
    "list_functions",
    "FraguaFunction",
]
