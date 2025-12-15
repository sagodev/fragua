"""Miner Class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, Union
from fragua.core.agent import FraguaAgent
from fragua.extract.params.generic_types import ExtractParamsT
from fragua.utils.logger import get_logger

if TYPE_CHECKING:
    from fragua.core.environment import FraguaEnvironment


logger = get_logger(__name__)


class Extractor(FraguaAgent[ExtractParamsT]):
    """
    Agent responsible for executing extraction workflows in Fragua.

    The Extractor applies extraction styles to external data sources
    (files, databases, APIs, etc.) and produces Box storage objects
    containing raw extracted data.

    This agent does not perform transformations or loading operations;
    its sole responsibility is data acquisition.
    """

    def __init__(self, name: str, environment: FraguaEnvironment):
        """
        Initialize the Extractor agent.

        Args:
            name: Logical name of the agent.
            environment: Active Fragua environment instance.
        """
        super().__init__(agent_name=name, environment=environment)
        self.role = "extractor"
        self.action = "extract"
        self.storage_type = "Box"

    def work(
        self,
        /,
        style: str,
        apply_to: Union[str, list[str], None] = None,
        save_as: Optional[str] = None,
        params: Optional[ExtractParamsT] = None,
        **kwargs: Any,
    ) -> None:
        """
        Execute an extraction workflow using a registered extract style.

        This method orchestrates the execution of an extraction style
        through the underlying agent workflow, producing a Box that
        can be stored in the Warehouse.

        Args:
            style: Name of the extraction style to apply.
            apply_to: Optional source identifier(s) to extract from.
            save_as: Optional target name under which the extracted
                Box will be stored in the Warehouse.
            params: ExtractParams instance defining configuration
                for the extraction process.
            **kwargs: Additional style-specific parameters.

        Returns:
            None
        """
        self._execute_workflow(style, save_as, params, **kwargs)
