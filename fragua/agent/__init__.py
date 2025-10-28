"""Fragua Agents package."""

# ------------------- Agent ------------------- #
from .agent import Agent

# ------------------- Roles ------------------- #
from .store_manager import StoreManager
from .agent_roles import (
    # Roles
    MinerRole,
    BlacksmithRole,
    TransporterRole,
    MasterRole,
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
    "MasterRole",
    # Roles Registry Functions
    "get_role",
    "list_roles",
    "register_role",
]
