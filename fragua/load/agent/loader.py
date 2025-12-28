"""Loader Agent Class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional, Union

from fragua.core.agent import FraguaAgent
from fragua.core.storage import Box, Container
from fragua.utils.logger import get_logger
from fragua.utils.types.enums import ActionType, FieldType, StorageType

if TYPE_CHECKING:
    from fragua.core.environment import FraguaEnvironment


logger = get_logger(__name__)

# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments


class Loader(FraguaAgent):
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
        super().__init__(agent_name=name, environment=environment)
        self.action = ActionType.LOAD
        self.storage_type = StorageType.CONTAINER

    # ----------------- Container helpers ----------------- #
    def _create_container(self, sources: Union[str, List[str]]) -> Container:
        container = self.create_storage(
            function_name=self.action,
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

    def _resolve_kwargs(self, box_name: str, **kwargs: Any) -> dict[str, Any]:
        resolved_kwargs = kwargs
        resolved_kwargs.setdefault(FieldType.SHEET_NAME.value, box_name)
        resolved_kwargs.setdefault(FieldType.TABLE_NAME.value, box_name)
        return resolved_kwargs

    # ----------------- Work method ----------------- #
    def work(
        self,
        target_type: str,
        apply_to: Union[str, List[str], None] = None,
        save_as: Optional[str] = None,
        input_data: Any = None,
        **kwargs: Any,
    ) -> None:
        if apply_to is None:
            raise TypeError("Missing required argument: 'apply_to'.")

        func = self._resolve_function(target_type)

        container = self._create_container(apply_to)

        for box_name in container.list_storages():
            box = container.get_storage(box_name)
            params = self._resolve_kwargs(box_name=box_name, **kwargs)

            func(input_data=box.data, **params)

            self._add_operation(target_type)
