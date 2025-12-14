"""Base Load Style Class."""

from abc import abstractmethod
from typing import Generic

from fragua.core.style import FraguaStyle

from fragua.load.params.generic_types import LoadParamsT
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


class LoadStyle(FraguaStyle, Generic[LoadParamsT]):
    """
    Base class for all Load styles in Fragua ETL.
    """

    @abstractmethod
    def load(self, params: LoadParamsT):
        """
        Load the given data to the target destination.
        Must be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement load()")

    def _run(self, params: LoadParamsT):
        logger.debug("Starting LoadStyle '%s' Load.", self.name)
        result = self.load(params)
        logger.debug("LoadStyle '%s' Load completed.", self.name)
        return result
