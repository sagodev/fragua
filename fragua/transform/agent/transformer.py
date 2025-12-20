"""Transformer Class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fragua.core.agent import FraguaAgent

from fragua.utils.logger import get_logger

if TYPE_CHECKING:
    from fragua.core.environment import FraguaEnvironment


logger = get_logger(__name__)


class Transformer(FraguaAgent):
    """
    Agent responsible for applying transformation styles to stored data.

    The Transformer retrieves data from the warehouse, applies the
    selected transformation style using the resolved parameters,
    and optionally stores the transformed result back into the warehouse.
    """

    def __init__(self, name: str, environment: FraguaEnvironment):
        """
        Initialize a Transformer agent.

        Args:
            name (str): Name of the transformer agent.
            environment (Environment): Execution environment instance.
        """
        super().__init__(agent_name=name, environment=environment)
        self.role = "transformer"
        self.action = "transform"
        self.storage_type = "Box"
