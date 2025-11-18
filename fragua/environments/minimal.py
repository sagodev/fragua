"""Minimal Environment Class."""

from __future__ import annotations

from fragua.environments.environment import Environment
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


class MinimalEnvironment(Environment):
    """
    A minimal Environment subclass that starts only with a Warehouse and WarehouseManager, but
    without Agents. Useful for flexible or custom setups.
    """

    def __init__(self, name: str, fg_reg: bool = False):
        super().__init__(name, env_type="minimal", fg_reg=fg_reg)

        warehouse = self.create_warehouse(f"{self.name}_warehouse")
        self.create_manager(f"{self.name}_manager", warehouse)

        logger.debug(
            "MinimalEnvironment '%s' initialized with no components.", self.name
        )
        logger.info("MinimalEnvironment '%s' is ready for manual setup.", self.name)
