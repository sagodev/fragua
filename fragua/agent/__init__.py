"""Fragua Agents package."""

# ------------------- Agents ------------------- #
from .agent import Agent
from .store_manager import StoreManager

# ------------------- Roles ------------------- #
from .agent_roles import (
    # Roles
    MinerRole,
    BlacksmithRole,
    TransporterRole,
    # Roles Registry Functions
    get_role,
    list_roles,
    register_role,
)

# ------------------- __all__ ------------------- #
__all__ = [
    # Agent Class
    "Agent",
    # Roles
    "StoreManager",
    "MinerRole",
    "BlacksmithRole",
    "TransporterRole",
    # Roles Registry Functions
    "get_role",
    "list_roles",
    "register_role",
]
