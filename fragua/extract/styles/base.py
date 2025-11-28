"""Base Extract Style Class."""

from typing import Generic
from fragua.core.style import ResultT, Style
from fragua.extract.params.generic_types import ExtractParamsT

from fragua.utils.logger import get_logger

logger = get_logger(__name__)


class ExtractStyle(Style[ExtractParamsT, ResultT], Generic[ExtractParamsT, ResultT]):
    """
    Base class for all extraction styles in Fragua ETL.

    Standard pipeline provided by Style:
        validate_params -> _run -> validate_result -> postprocess
    """

    def extract(self, params: ExtractParamsT) -> ResultT:
        """
        Base extract method. Should be implemented by subclasses
        to call the appropriate registered function.
        """
        raise NotImplementedError

    def _run(self, params: ExtractParamsT) -> ResultT:
        logger.debug("Starting ExtractStyle '%s' extraction.", self.style_name)
        result = self.extract(params)
        logger.debug("ExtractStyle '%s' extraction completed.", self.style_name)
        return result
