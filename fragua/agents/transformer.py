"""Transformer Class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from fragua.agents.agent import Agent

from fragua.params.transform_params import TransformParams
from fragua.utils.logger import get_logger

if TYPE_CHECKING:
    from fragua.environments.environment import Environment


logger = get_logger(__name__)


class Transformer(Agent[TransformParams]):
    """Agent that applies transform styles to data for transformation."""

    def __init__(self, name: str, environment: Environment):
        super().__init__(name=name, environment=environment)
        self.role = "transformer"
        self.action = "transform"
        self.storage_type = "Box"

    def work(
        self,
        /,
        style: str,
        apply_to: str | list[str] | None = None,
        save_as: str | None = None,
        params: TransformParams | None = None,
        **kwargs: Any,
    ) -> None:
        """Execute the agent's task using the action and style defined by transformer role."""

        if isinstance(apply_to, str):
            storage = self.get_from_warehouse(apply_to)
            data = storage.data
            kwargs["data"] = data
            self._execute_workflow(style, save_as, params, **kwargs)
