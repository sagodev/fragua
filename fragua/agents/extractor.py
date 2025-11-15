"""Miner Class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from fragua.agents.agent import Agent
from fragua.params.extract_params import ExtractParams
from fragua.utils.logger import get_logger

if TYPE_CHECKING:
    from fragua.environments.environment import Environment


logger = get_logger(__name__)


class Extractor(Agent[ExtractParams]):
    """Agent that applies extraction styles to data sources for extraction."""

    def __init__(self, name: str, environment: Environment):
        super().__init__(name=name, environment=environment)
        self.role = "extractor"
        self.action = "extract"
        self.storage_type = "Box"

    def work(
        self,
        /,
        style: str,
        apply_to: str | list[str] | None = None,
        save_as: str | None = None,
        params: ExtractParams | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Execute the extraction workflow using an ExtractParams instance.
        """
        self._execute_workflow(style, save_as, params, **kwargs)
