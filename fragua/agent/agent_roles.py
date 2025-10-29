"""
Agent role classes with different behavior configurations.
"""

from typing import Any

ROLE_REGISTRY: dict[str, dict[str, Any]] = {}


def register_role(
    role_name: str,
    action: str,
    storage_type: str,
    allowed_functions: tuple[str, ...] = (),
) -> Any:
    """
    Decorator to register an Agent role in the global registry.
    """

    def decorator(cls: type) -> type:
        ROLE_REGISTRY[role_name.lower()] = {
            "action": action,  # Always str
            "storage_type": storage_type,
            "allowed_functions": allowed_functions,
        }
        return cls

    return decorator


def get_role(role_name: str) -> dict[str, Any]:
    """Retrieve a registered agent role by name."""
    role_name_lower = role_name.lower()
    if role_name_lower not in ROLE_REGISTRY:
        raise KeyError(f"Role '{role_name}' not registered.")
    return ROLE_REGISTRY[role_name_lower]


def list_roles() -> list[str]:
    """List all registered agent roles."""
    return list(ROLE_REGISTRY.keys())


# ---------------------- Roles Definition ---------------------- #


@register_role(
    "miner",
    action="mine",
    storage_type="Wagon",
    allowed_functions=(
        "_generate_operation_metadata",
        "work",
        "create_storage",
        "store_result",
        "get_operations",
    ),
)
class MinerRole:
    """Miner agent role."""


@register_role(
    "blacksmith",
    action="forge",
    storage_type="Box",
    allowed_functions=(
        "work",
        "create_storage",
        "store_result",
        "get_operations",
        "_generate_operation_metadata",
    ),
)
class BlacksmithRole:
    """Blacksmith agent role."""


@register_role(
    "transporter",
    action="deliver",
    storage_type="*",
    allowed_functions=(
        "_generate_operation_metadata",
        "work",
        "create_storage",
    ),
)
class TransporterRole:
    """Transporter agent role."""


@register_role(
    "master",
    action="*",
    storage_type="*",
    allowed_functions=("*",),
)
class MasterRole:
    """Master agent role with full access to all functions."""

    # Dict for storage type
    style_prefix_to_storage = {
        "mine": "Wagon",
        "forge": "Box",
        "deliver": "Container",
    }

    # Dict for action type
    style_prefix_to_action = {
        "mine": "mine",
        "forge": "forge",
        "deliver": "deliver",
    }
