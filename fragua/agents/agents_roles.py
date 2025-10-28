"""
Agent role classes with different behavior configurations.
"""

from fragua.core.agent import register_role


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
