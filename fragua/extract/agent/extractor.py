"""Miner Class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from fragua.core.agent import Agent
from fragua.extract.params.generic_types import ExtractParamsT
from fragua.utils.logger import get_logger

if TYPE_CHECKING:
    from fragua.core.environment import Environment


logger = get_logger(__name__)


class Extractor(Agent[ExtractParamsT]):
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
        params: ExtractParamsT | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Execute the extraction workflow using an ExtractParams instance.
        """
        self._execute_workflow(style, save_as, params, **kwargs)
