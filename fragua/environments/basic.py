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

    def __init__(self, env_name: str, fg_reg: bool = False):
        super().__init__(env_name=env_name, env_type="basic", fg_reg=fg_reg)

        logger.debug("Creating BasicEnvironment '%s'...", self.name)

        self.create_extractor(f"{env_name}_etr")
        self.create_transformer(f"{env_name}_tfr")
        self.create_loader(f"{env_name}_ldr")

        logger.info(
            "Basic environment '%s' created successfully with warehouse, manager, and 3 agents.",
            self.name,
        )
