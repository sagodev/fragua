"""Miner Class."""

from __future__ import annotations

from typing import TYPE_CHECKING
from fragua.core.agent import FraguaAgent
from fragua.utils.logger import get_logger

if TYPE_CHECKING:
    from fragua.core.environment import FraguaEnvironment


logger = get_logger(__name__)


class Extractor(FraguaAgent):
    """
    Agent responsible for executing extraction workflows in Fragua.

    The Extractor applies extraction styles to external data sources
    (files, databases, APIs, etc.) and produces Box storage objects
    containing raw extracted data.

    This agent does not perform transformations or loading operations;
    its sole responsibility is data acquisition.
    """

    def __init__(self, name: str, environment: FraguaEnvironment):
        """
        Initialize the Extractor agent.

        Args:
            name: Logical name of the agent.
            environment: Active Fragua environment instance.
        """
        super().__init__(agent_name=name, environment=environment)
        self.role = "extractor"
        self.action = "extract"
        self.storage_type = "Box"
