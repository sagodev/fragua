"""Fragua Agents package."""

# ------------------- Agent ------------------- #
from .agent import Agent

# ------------------- Roles ------------------- #
from .agent_roles import (
    # Roles
    StoreManagerRole,
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
    "StoreManagerRole",
    "MinerRole",
    "BlacksmithRole",
    "TransporterRole",
    "MasterRole",
    # Roles Registry Functions
    "get_role",
    "list_roles",
    "register_role",
]
