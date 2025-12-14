"""Loader Class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional, Union
from fragua.core.agent import FraguaAgent

from fragua.load.params.generic_types import LoadParamsT
from fragua.load.params.load_params import ExcelLoadParams
from fragua.core.storage import Box, Container
from fragua.utils.logger import get_logger

if TYPE_CHECKING:
    from fragua.core.environment import Environment


logger = get_logger(__name__)


class Loader(FraguaAgent):
    """Agent that applies extraction styles to data sources for loading."""

    def __init__(self, name: str, environment: Environment):
        super().__init__(agent_name=name, environment=environment)
        self.role: str = "loader"
        self.action: str = "load"
        self.storage_type: str = "Container"

    def create_container(self, content: Union[str, List[str]]) -> Container:
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
        apply_to: Union[str | list[str], None] = None,
        save_as: Optional[str] = None,
        params: Optional[LoadParamsT] = None,
        **kwargs: Any,
    ) -> None:
        """
        Execute the loader workflow for one or multiple stored objects.

        This method loads one or more Box objects from the warehouse into
        a Container and applies the selected load style to each storage
        using the resolved parameters.
        """

        if apply_to is None:
            raise TypeError("Missing required attribute: 'apply_to'.")

        style = style.lower()

        # -------- Resolve style --------
        style_instance = self._instantiate_style(style)

        # -------- Create container --------
        container: Container = self.create_container(apply_to)

        # -------- Apply style to each storage --------
        for name in container.list_storages():
            box = container.get_storage(name)

            # -------- Resolve params --------
            if params is None:
                kwargs["data"] = box.data
                params_instance = self._instantiate_params(style, None, **kwargs)
            else:
                params_instance = params

            # -------- Excel-specific adjustment --------
            if isinstance(params_instance, ExcelLoadParams):
                if not getattr(params_instance, "sheet_name", None):
                    params_instance.sheet_name = name

            # -------- Execute style --------
            style_instance.use(params_instance)

            # -------- Log operation --------
            self._add_operation(style, params_instance)
