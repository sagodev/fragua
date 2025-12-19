"""
Utility functions for configuration handling.
This module provides helper functions to convert dictionaries
into FraguaSet objects, facilitating the management of
configuration data.
"""

from typing import Any, Dict

from fragua.core.fragua_class import FraguaClass
from fragua.core.fragua_instance import FraguaInstance
from fragua.core.set import FraguaSet


def to_fragua_set(set_name: str, dict_data: Dict[str, Any]) -> FraguaSet:
    """
    Convert a dictionary of components into a FraguaSet.

    The method automatically detects whether the components are
    classes or instances based on the type of the first element.

    Args:
        set_name: Name of the FraguaSet to create.
        dict_data: Dictionary mapping keys to components.

    Returns:
        FraguaSet containing the provided components.
    """
    # Infer content_kind
    first_value = next(iter(dict_data.values()), None)
    if first_value is None:
        content_kind = "class"  # default for empty dict
    elif isinstance(first_value, type) and issubclass(first_value, FraguaClass):
        content_kind = "class"
    elif isinstance(first_value, FraguaInstance):
        content_kind = "instance"
    else:
        # fallback: treat as 'class' by default
        content_kind = "class"

    # Create set and add elements
    set_instance = FraguaSet(set_name=set_name, content_kind=content_kind)
    for key, value in dict_data.items():
        set_instance.add(key, value)

    return set_instance
