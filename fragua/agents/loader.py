"""Loader Class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, List
from fragua.agents.agent import Agent

from fragua.params.load_params import ExcelLoadParams, LoadParams
from fragua.storages.storage_types import Box, Container
from fragua.utils.logger import get_logger

if TYPE_CHECKING:
    from fragua.environments.environment import Environment


logger = get_logger(__name__)


class Loader(Agent[LoadParams]):
    """Agent that applies extraction styles to data sources for loading."""

    def __init__(self, name: str, environment: Environment):
        super().__init__(name=name, environment=environment)
        self.role: str = "loader"
        self.action: str = "load"
        self.storage_type: str = "Container"

    def create_container(self, content: str | List[str]) -> Container:
        """Create and fill a Container using stored Box objects."""

        container = self.create_storage(data=None)

        if not isinstance(container, Container):
            raise TypeError(
                f"Expected a Container, got {type(container).__name__} ({container})"
            )

        storage_names = [content] if isinstance(content, str) else content

        for name in storage_names:
            storage = self.get_from_warehouse(name)

            if not isinstance(storage, Box):
                raise TypeError(
                    f"Type {type(storage).__name__} can't be stored in a container."
                )

            container.add_storage(name, storage)

        return container

    def work(
        self,
        /,
        style: str,
        apply_to: str | list[str] | None = None,
        save_as: str | None = None,
        params: LoadParams | None = None,
        **kwargs: Any,
    ) -> None:
        """Execute the agent's task using the action and style defined by loader role."""

        if apply_to is None:
            raise TypeError("Missing required attribute: 'content'.")

        style = style.lower()

        # ----------------- Style class -----------------
        style_cls = self.get_registred_class("styles", style, self.action)

        # ----------------- Create Storage -----------------
        container: Container = self.create_container(apply_to)

        # ----------------- Apply Style for each storage -----------------
        for name in container.list_storages():

            # -------- Build params --------
            if params is None:
                params_cls = self.get_registred_class("params", style, self.action)
                kwargs["data"] = container.get_storage(name).data
                params_instance = params_cls(**kwargs)
            else:
                params_instance = params

            # -------- Assign sheet_name based on storage name --------
            if isinstance(params_instance, ExcelLoadParams):
                if getattr(params_instance, "sheet_name", None) in (None, ""):
                    params_instance.sheet_name = name

            # ----------------- Instantiate the style -----------------
            style_instance = style_cls(style)
            style_instance.use(params_instance)

            # ----------------- Generate operation metadata -----------------
            self._add_operation(style, params_instance)
