"""
Base Transform Style Class.

Defines the abstract contract for all transformation styles
within the Fragua ETL framework.
"""

from abc import abstractmethod
from typing import Any, Generic
from fragua.core.style import FraguaStyle
from fragua.transform.params.generic_types import TransformParamsT
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


class TransformStyle(FraguaStyle[TransformParamsT], Generic[TransformParamsT]):
    """
    Base class for all transformation styles in Fragua ETL.

    A TransformStyle encapsulates the orchestration logic required
    to apply one or more transformation functions to a dataset.
    Concrete implementations must define how transformation
    parameters are processed and which registered functions
    are executed.
    """

    @abstractmethod
    def transform(self, params: TransformParamsT) -> Any:
        """
        Apply the transformation logic to the given parameters.

        This method must be implemented by subclasses and is
        responsible for invoking the appropriate registered
        transformation function(s).

        Args:
            params (TransformParamsT):
                Parameter object containing the input data and
                transformation configuration.

        Returns:
            Any:
                The result of the transformation, typically a
                transformed pandas DataFrame.
        """
        raise NotImplementedError("Subclasses must implement transform()")

    def _run(self, params: TransformParamsT) -> Any:
        """
        Execute the transformation workflow with logging and lifecycle handling.

        This internal method is invoked by the Fragua execution
        pipeline and should not be overridden by subclasses.

        Args:
            params (TransformParamsT):
                Parameter object used during transformation.

        Returns:
            Any:
                The result returned by the concrete transform implementation.
        """
        logger.debug("Starting TransformStyle '%s' transformation.", self.name)
        result = self.transform(params)
        logger.debug("TransformStyle '%s' transformation completed.", self.name)
        return result
