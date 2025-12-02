"""Basic environment for Fragua."""

from __future__ import annotations

from fragua.core.environment import Environment
from fragua.utils.logger import get_logger


logger = get_logger(__name__)


class BasicEnvironment(Environment):
    """
    Predefined environment with the essential Fragua setup:
    - 1 Warehouse
    - 1 WarehouseManager
    - 1 Extractor
    - 1 Transformer
    - 1 Loader
    """

    def __init__(self, name: str, fg_reg: bool = False):
        super().__init__(name, env_type="basic", fg_reg=fg_reg)

        logger.debug("Creating BasicEnvironment '%s'...", self.name)

        self.create_extractor(f"{name}_etr")
        self.create_transformer(f"{name}_tfr")
        self.create_loader(f"{name}_ldr")

        self.add_registries()

        logger.info(
            "Basic environment '%s' created successfully with warehouse, manager, and 3 agents.",
            self.name,
        )
