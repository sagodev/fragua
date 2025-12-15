"""Base Load Style Class."""

from abc import abstractmethod
from typing import Any, Generic

from fragua.core.style import FraguaStyle

from fragua.load.params.generic_types import LoadParamsT
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


class LoadStyle(FraguaStyle[LoadParamsT], Generic[LoadParamsT]):
    """
    Abstract base class for all load styles in Fragua ETL.

    A LoadStyle defines how data is written to a target destination
    (files, databases, APIs, etc.) by coordinating parameter handling
    and delegating execution to the corresponding load function.
    """

    @abstractmethod
    def load(self, params: LoadParamsT) -> Any:
        """
        Execute the load operation using the provided parameters.

        This method must be implemented by subclasses and should
        contain the concrete logic required to persist data into
        the target system.

        Args:
            params (LoadParamsT):
                Parameters defining how and where data should be loaded.
        """
        raise NotImplementedError("Subclasses must implement load()")

    def _run(self, params: LoadParamsT) -> Any:
        """
        Internal execution pipeline for load styles.

        This method wraps the concrete `load` implementation with
        logging and is invoked by the public `use()` method inherited
        from FraguaStyle.

        Args:
            params (LoadParamsT):
                Load parameters passed to the style.

        Returns:
            Any:
                Result returned by the concrete load implementation.
        """
        logger.debug("Starting LoadStyle '%s' load.", self.name)
        result = self.load(params)
        logger.debug("LoadStyle '%s' load completed.", self.name)
        return result
