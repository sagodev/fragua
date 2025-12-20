"""Transformer Class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pandas import DataFrame
from fragua.core.agent import FraguaAgent

from fragua.core.params import FraguaParams
from fragua.utils.logger import get_logger

if TYPE_CHECKING:
    from fragua.core.environment import FraguaEnvironment


logger = get_logger(__name__)

# pylint: disable=too-many-arguments


class Transformer(FraguaAgent):
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
        style: str,
        apply_to: str | list[str] | None = None,
        save_as: str | None = None,
        params: FraguaParams | None = None,
        input_data: DataFrame | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Execute a transformation workflow.
        This method orchestrates the execution of a transformation style.
        Args:
            style (str): Name of the transformation style to apply.
            apply_to (str | list[str] | None): Target data identifiers.
            save_as (str | None): Optional name to save the transformed data.
            params (FraguaParams | None): Optional parameters for the transformation.
            input_data (DataFrame | None): Optional input data for transformation.
            **kwargs: Additional keyword arguments.
        Returns:
            None
        """
        super().work(
            style=style,
            apply_to=apply_to,
            save_as=save_as,
            params=params,
            input_data=input_data,
            **kwargs,
        )
