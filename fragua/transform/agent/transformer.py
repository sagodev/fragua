"""Transformer Class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, Union
from fragua.core.agent import FraguaAgent

from fragua.transform.params.generic_types import TransformParamsT
from fragua.utils.logger import get_logger

if TYPE_CHECKING:
    from fragua.core.environment import FraguaEnvironment


logger = get_logger(__name__)


class Transformer(FraguaAgent[TransformParamsT]):
    """
    Agent responsible for applying transformation styles to stored data.

    The Transformer retrieves data from the warehouse, applies the
    selected transformation style using the resolved parameters,
    and optionally stores the transformed result back into the warehouse.
    """

    def __init__(self, name: str, environment: FraguaEnvironment):
        """
        Initialize a Transformer agent.

        Args:
            name (str): Name of the transformer agent.
            environment (Environment): Execution environment instance.
        """
        super().__init__(agent_name=name, environment=environment)
        self.role = "transformer"
        self.action = "transform"
        self.storage_type = "Box"

    def work(
        self,
        /,
        style: str,
        apply_to: Union[str | list[str], None] = None,
        save_as: Optional[str] = None,
        params: Optional[TransformParamsT] = None,
        **kwargs: Any,
    ) -> None:
        """
        Execute a transformation workflow.

        This method retrieves the target data from the warehouse,
        resolves the transformation style and parameters, and
        applies the transformation logic accordingly.

        Args:
            style (str):
                Name of the transformation style to apply.
            apply_to (str | list[str] | None):
                Name of the storage object(s) in the warehouse to transform.
            save_as (Optional[str]):
                Optional name under which to store the transformed result.
            params (Optional[TransformParamsT]):
                Explicit transformation parameters instance.
            **kwargs:
                Additional keyword arguments used to build parameters
                when `params` is not provided.
        """

        if isinstance(apply_to, str):
            storage = self.get_from_warehouse(apply_to)
            data = storage.data
            kwargs["data"] = data

            self._execute_workflow(style, save_as, params, **kwargs)
