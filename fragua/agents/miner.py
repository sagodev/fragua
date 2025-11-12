"""Miner Class."""

from __future__ import annotations

from typing import Any
from fragua.agents.agent import Agent

from fragua.environments.environment import Environment
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


class Miner(Agent):
    """Agent that applies extraction styles to data sources for extraction."""

    def __init__(self, name: str, environment: Environment):
        super().__init__(name=name, environment=environment)
        self.role = "miner"
        self.action = "extract"
        self.storage_type = "Wagon"

    def work(
        self,
        /,
        style: str,
        save_as: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Execute the agent's task using the action and style defined by its role."""
        self._execute_workflow(style, save_as, **kwargs)
