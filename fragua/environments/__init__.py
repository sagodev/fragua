"""Fragua environment factory and exports."""

from typing import Dict, Type
from fragua.environments.environment import Environment
from fragua.environments.basic import BasicEnvironment
from fragua.environments.minimal import MinimalEnvironment

# Registry of available environment types
ENVIRONMENT_TYPES: Dict[str, Type[Environment]] = {
    "minimal": MinimalEnvironment,
    "basic": BasicEnvironment,
}


def create_fragua(
    name: str, env_type: str = "basic", fg_reg: bool = False
) -> Environment:
    """
    Create a Fragua environment with a specific configuration.

    Args:
        name (str): Environment name.
        env_type (str): Environment type ("basic", "minimal", ...).

    Returns:
        Environment: Instantiated and configured environment.

    Raises:
        ValueError: If env_type is not a recognized type.
    """
    env_type = env_type.lower()
    if env_type not in ENVIRONMENT_TYPES:
        raise ValueError(
            f"Unknown environment type '{env_type}'. "
            f"Available: {list(ENVIRONMENT_TYPES.keys())}"
        )

    env_class = ENVIRONMENT_TYPES[env_type]
    environment = env_class(name, fg_reg=fg_reg)

    return environment


__all__ = [
    "Environment",
    "MinimalEnvironment",
    "BasicEnvironment",
    "create_fragua",
]
