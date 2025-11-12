"""Haulier Class."""

from __future__ import annotations

from typing import Any, List
from fragua.agents.agent import Agent
from fragua.environments.environment import Environment
from fragua.storages.storage_types import Box, Container, Wagon
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


class Haulier(Agent):
    """Agent that applies extraction styles to data sources for loading."""

    def __init__(self, name: str, environment: Environment):
        super().__init__(name=name, environment=environment)
        self.role: str = "haulier"
        self.action: str = "load"
        self.storage_type: str = "Container"

    def create_container(self, content: str | List[str]) -> Container:
        """Create and fill a Container using stored Wagon/Box objects."""

        container = self.create_storage(data=None)

        if not isinstance(container, Container):
            raise TypeError(
                f"Expected a Container, got {type(container).__name__} ({container})"
            )

        storage_names = [content] if isinstance(content, str) else content

        for name in storage_names:
            storage = self.get_from_store(name)

            if not isinstance(storage, (Wagon, Box)):
                raise TypeError(
                    f"Type {type(storage).__name__} can't be stored in a container."
                )

            container.add_storage(name, storage)

        return container

    def work(
        self,
        /,
        style: str,
        save_as: str | None = None,
        content: str | list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """Execute the agent's task using the action and style defined by haulier role."""

        if content is None:
            raise TypeError("Missing required attribute: 'content'.")

        style = style.lower()

        # ----------------- Style Instance -----------------
        style_instance = self.get_registred_class("load", style, self.action)

        # ----------------- Create Storage -----------------
        container: Container = self.create_container(content)

        # ----------------- Apply Style for each storage -----------------
        for name in container.list_storages():

            kwargs["data"] = container.get_storage(name).data

            if style == "excel":
                kwargs["sheet_name"] = name

            params_instance = self.get_registred_class("load", style, self.action)

            style_instance.use(params_instance)

            # ----------------- Generate operation metadata -----------------
            self._add_operation(style, params_instance)
