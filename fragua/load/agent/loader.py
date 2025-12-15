"""
Loader Agent Class.

Defines the Loader agent responsible for applying load styles to
stored Box objects and persisting their data into target destinations
(e.g. files, databases, external systems).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional, Union
from fragua.core.agent import FraguaAgent

from fragua.load.params.generic_types import LoadParamsT
from fragua.load.params.load_params import ExcelLoadParams
from fragua.core.storage import Box, Container
from fragua.utils.logger import get_logger

if TYPE_CHECKING:
    from fragua.core.environment import FraguaEnvironment


logger = get_logger(__name__)


class Loader(FraguaAgent[LoadParamsT]):
    """
    Loader agent responsible for executing load workflows.

    This agent:
    - retrieves Box objects from the Warehouse
    - groups them into a Container
    - resolves load styles and parameters
    - executes the load operation for each stored object
    """

    def __init__(self, name: str, environment: FraguaEnvironment):
        """
        _toggleLoader agent initialization.

                Args:
                    name (str): Agent identifier.
                    environment (Environment): Active Fragua environment.
        """
        super().__init__(agent_name=name, environment=environment)
        self.role: str = "loader"
        self.action: str = "load"
        self.storage_type: str = "Container"

    def create_container(self, content: Union[str, List[str]]) -> Container:
        """
        Create a Container populated with Box objects from the warehouse.

        Args:
            content (Union[str, List[str]]): One or more Box names
                to retrieve from the warehouse.

        Returns:
            Container: A container holding the resolved Box objects.

        Raises:
            TypeError: If the created storage is not a Container or
                if any resolved object is not a Box.
        """
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
        Execute a load workflow for one or more stored Box objects.

        Workflow steps:
            1. Resolve the load style.
            2. Collect Box objects into a Container.
            3. Resolve or instantiate load parameters.
            4. Apply the load style to each Box's data.
            5. Register the operation in the agent log.

        Args:
            style (str): Load style identifier (e.g. "excel", "sql").
            apply_to (Union[str, list[str]]): Name(s) of Box objects
                to be loaded.
            save_as (Optional[str]): Optional storage alias (reserved).
            params (Optional[LoadParamsT]): Explicit load parameters.
            **kwargs: Additional keyword arguments used to build params.

        Raises:
            TypeError: If required arguments are missing or invalid.
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
