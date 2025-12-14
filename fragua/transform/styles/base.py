"""Base Transform Style Class."""

from abc import abstractmethod
from typing import Generic
from fragua.core.style import FraguaStyle
from fragua.transform.params.generic_types import TransformParamsT
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


class TransformStyle(FraguaStyle, Generic[TransformParamsT]):
    """
    Base class for all transformation styles in Fragua ETL.
    """

    @abstractmethod
    def transform(self, params: TransformParamsT):
        """
        Base transform method. Should be implemented by subclasses
        to call the appropriate registered function.
        """
        raise NotImplementedError

    def _run(self, params: TransformParamsT):
        logger.debug("Starting TransformStyle '%s' transformation.", self.name)
        result = self.transform(params)
        logger.debug("TransformStyle '%s' transformation completed.", self.name)
        return result
