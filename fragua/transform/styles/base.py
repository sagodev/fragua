"""Base Transform Style Class."""

from abc import abstractmethod
from typing import Generic
from fragua.core.style import ResultT, Style
from fragua.transform.params.generic_types import TransformParamsT
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


class TransformStyle(
    Style[TransformParamsT, ResultT], Generic[TransformParamsT, ResultT]
):
    """
    Base class for all transformation styles in Fragua ETL.

    Standard pipeline provided by Style:
        validate_params -> _run -> validate_result -> postprocess
    """

    @abstractmethod
    def transform(self, params: TransformParamsT) -> ResultT:
        """
        Base transform method. Should be implemented by subclasses
        to call the appropriate registered function.
        """
        raise NotImplementedError

    def _run(self, params: TransformParamsT) -> ResultT:
        logger.debug("Starting TransformStyle '%s' transformation.", self.style_name)
        result = self.transform(params)
        logger.debug("TransformStyle '%s' transformation completed.", self.style_name)
        return result
