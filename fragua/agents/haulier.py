"""Haulier Class."""

from __future__ import annotations

from typing import Any, List
from fragua.agents.agent import Agent
from fragua.agents.store_manager import StoreManager
from fragua.store.storage_types import Box, Container, Wagon
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


class Haulier(Agent):
    """Agent that applies extraction styles to data sources for extraction."""

    def __init__(self, name: str, store_manager: StoreManager):
        super().__init__(name=name, store_manager=store_manager)
        self.role: str = "haulier"
        self.action: str = "deliver"
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
        style_instance = self._get_style(style)

        # ----------------- Create Storage -----------------
        container: Container = self.create_container(content)

        # ----------------- Apply Style for each storage -----------------
        for name in container.list_storages():

            kwargs["data"] = container.get_storage(name).data

            if style == "excel":
                kwargs["sheet_name"] = name

            params_instance = self._get_params(style, **kwargs)

            style_instance.use(params_instance)

            # ----------------- Generate operation metadata -----------------
            self._add_operation(style, params_instance)
