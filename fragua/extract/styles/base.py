"""Base Extract Style Class."""

from abc import abstractmethod
from typing import Any, Generic

from fragua.core.style import FraguaStyle
from fragua.extract.params.generic_types import ExtractParamsT
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


class ExtractStyle(FraguaStyle[ExtractParamsT], Generic[ExtractParamsT]):
    """
    Abstract base class for all extraction styles in Fragua.

    An ExtractStyle is responsible for orchestrating the extraction
    workflow by coordinating extract functions and parameters.
    It does not perform the extraction itself, but delegates the
    execution to the appropriate ExtractFunction implementation.
    """

    @abstractmethod
    def extract(self, params: ExtractParamsT) -> Any:
        """
        Execute the extraction logic for this style.

        This method must be implemented by subclasses and should:
        - validate or prepare input parameters
        - resolve the appropriate extract function
        - invoke the function execution

        Args:
            params (ExtractParamsT): Parameters required by the extract style.

        Returns:
            Any: The extracted data produced by the underlying extract function.
        """
        raise NotImplementedError

    def _run(self, params: ExtractParamsT) -> Any:
        """
        Internal execution hook invoked by the FraguaStyle pipeline.

        Wraps the extract execution with logging and returns the extracted result.
        """
        logger.debug("Starting ExtractStyle '%s' extraction.", self.name)
        result = self.extract(params)
        logger.debug("ExtractStyle '%s' extraction completed.", self.name)
        return result
