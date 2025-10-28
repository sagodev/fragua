"""
Agent role classes with different behavior configurations.
"""

from typing import Any

ROLE_REGISTRY: dict[str, dict[str, str | tuple[str, ...]]] = {}


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
            "action": action,
            "storage_type": storage_type,
            "allowed_functions": allowed_functions,
        }
        return cls

    return decorator


def get_role(role_name: str) -> dict[str, str | tuple[str, ...]]:
    """Retrieve a agent role by name."""
    if role_name.lower() not in ROLE_REGISTRY:
        raise KeyError(f"Role '{role_name}' not registered.")
    return ROLE_REGISTRY[role_name.lower()]


def list_roles() -> list[str]:
    """list all agent roles."""
    return list(ROLE_REGISTRY.keys())


@register_role(
    "miner",
    action="mine",
    storage_type="Wagon",
    allowed_functions=("work", "create_storage", "store_result"),
)
class MinerRole:
    """Miner agent role."""


@register_role(
    "blacksmith",
    action="forge",
    storage_type="Box",
    allowed_functions=("work", "create_storage", "store_result"),
)
class BlacksmithRole:
    """Blacksmith agent role."""


@register_role(
    "transporter",
    action="deliver",
    storage_type="Container",
    allowed_functions=("work", "create_storage", "store_result"),
)
class TransporterRole:
    """Transporter agent role."""
