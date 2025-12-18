"""
Loader Agent Class.

Defines the Loader agent responsible for applying load styles to
stored Box objects and persisting their data into target destinations
(e.g. files, databases, external systems).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional, Union

from fragua.core.agent import FraguaAgent
from fragua.core.params import FraguaParamsT
from fragua.core.storage import Box, Container
from fragua.utils.logger import get_logger

if TYPE_CHECKING:
    from fragua.core.environment import FraguaEnvironment


logger = get_logger(__name__)


class Loader(FraguaAgent[FraguaParamsT]):
    """
    Loader agent responsible for executing load workflows.

    The Loader:
    - retrieves Box objects from the Warehouse
    - groups them into a Container
    - executes load functions over each Box
    - does not generate new data storages, but performs side effects
      (files, databases, external systems)
    """

    def __init__(self, name: str, environment: FraguaEnvironment) -> None:
        """
        Initialize the Loader agent.

        Args:
            name: Agent identifier.
            environment: Active Fragua environment.
        """
        super().__init__(agent_name=name, environment=environment)
        self.role = "loader"
        self.action = "load"
        self.storage_type = "Container"

    # ----------------- Container helpers ----------------- #
    def _create_container(self, sources: Union[str, List[str]]) -> Container:
        """
        Create a Container populated with Box objects from the warehouse.

        Args:
            sources: One or more storage names to retrieve.

        Returns:
            A Container holding the resolved Box objects.

        Raises:
            TypeError: If resolved objects are not Box instances.
        """
        container = self.create_storage(
            style_name=self.action,
            storage_name="load_container",
            data=None,
        )

        if not isinstance(container, Container):
            raise TypeError(f"Expected Container, got {type(container).__name__}.")

        names = [sources] if isinstance(sources, str) else sources

        for name in names:
            box = self.get_from_warehouse(name)

            if not isinstance(box, Box):
                raise TypeError(f"Storage '{name}' is not a Box and cannot be loaded.")

            container.add_storage(name, box)

        return container

    # ----------------- Work method ----------------- #
    def work(
        self,
        style: str,
        apply_to: Union[str, List[str], None] = None,
        save_as: Optional[str] = None,
        params: Optional[FraguaParamsT] = None,
        input_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """
        Execute a load workflow.

        The Loader differs from Extract/Transform in that:
        - it operates on existing Box objects
        - it executes load functions for side effects
        - it does not persist new storages automatically

        Args:
            style: Load style identifier.
            apply_to: One or more Box names to load.
            save_as: Reserved (not used for load operations).
            params: Optional pre-instantiated Params object.
            **kwargs: Additional arguments for Params resolution.

        Raises:
            TypeError: If apply_to is missing.
        """
        if apply_to is None:
            raise TypeError("Missing required argument: 'apply_to'.")

        style = style.lower()

        # 1. Resolve style specification
        style_spec = self._resolve_style(style)

        # 2. Resolve function
        func = self._resolve_function(style_spec["function_key"])

        # 3. Create container
        container = self._create_container(apply_to)

        # 4. Execute load for each Box
        for name in container.list_storages():
            box = container.get_storage(name)

            # Resolve params
            params_instance = self._resolve_params(
                style,
                params,
                data=box.data,
                **kwargs,
            )

            # Optional sheet_name alignment (Excel-like loaders)
            if hasattr(params_instance, "sheet_name") and not getattr(
                params_instance, "sheet_name"
            ):
                setattr(params_instance, "sheet_name", name)

            # Execute load function
            func(input_data=box.data, params=params_instance, context=self)

            # Log operation (no storage created)
            self._add_operation(style, params_instance)
