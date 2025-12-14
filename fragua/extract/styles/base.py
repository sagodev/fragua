"""Base Extract Style Class."""

from abc import abstractmethod
from typing import Generic
from fragua.core.style import FraguaStyle
from fragua.extract.params.generic_types import ExtractParamsT
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


class ExtractStyle(FraguaStyle, Generic[ExtractParamsT]):
    """
    Base class for all extraction styles in Fragua ETL.
    """

    @abstractmethod
    def extract(self, params: ExtractParamsT):
        """
        Base extract method. Should be implemented by subclasses
        to call the appropriate registered function.
        """
        raise NotImplementedError

    def _run(self, params: ExtractParamsT):
        logger.debug("Starting ExtractStyle '%s' extraction.", self.name)
        result = self.extract(params)
        logger.debug("ExtractStyle '%s' extraction completed.", self.name)
        return result
