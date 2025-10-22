"""
Base ExtractionStyle class for Fragua Miners.
Contains common utilities for extraction workflows.
"""

from abc import abstractmethod
from typing import Any, Dict, Type, Callable, Generic
from datetime import datetime, timezone
from fragua.core.base_style import BaseStyle, ResultT
from fragua.params.mine_params import MineParamsT
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------- #
# Type Variables
# ---------------------------------------------------------------------- #

# Registry for dynamic loading
MINESTYLE_REGISTRY: Dict[str, Type["MineStyle[Any, Any]"]] = {}


def register_mine_style(
    name: str,
) -> Callable[[Type["MineStyle[Any, Any]"]], Type["MineStyle[Any, Any]"]]:
    """
    Decorator to register a MineStyle subclass.
    """

    def wrapper(
        cls: Type["MineStyle[Any, Any]"],
    ) -> Type["MineStyle[Any, Any]"]:
        MINESTYLE_REGISTRY[name] = cls
        logger.debug("Registered MineStyle: %s", name)
        return cls

    return wrapper


# ---------------------------------------------------------------------- #
# Base MineStyle
# ---------------------------------------------------------------------- #
class MineStyle(BaseStyle[MineParamsT, ResultT], Generic[MineParamsT, ResultT]):
    """
    Base class for all extraction styles in Fragua ETL.

    Provides the standardized pipeline:
        validate_params -> extract -> validate_result -> postprocess
    """

    def __init__(self, style_name: str):
        super().__init__(style_name)
        self.created_at = datetime.now(timezone.utc)
        self.metadata: Dict[str, Any] = {"created_at": self.created_at}

    # ---------------------------------------------------------------------- #
    # Abstract extraction method
    # ---------------------------------------------------------------------- #
    @abstractmethod
    def extract(self, params: MineParamsT) -> ResultT:
        """
        Extract data according to source parameters.
        Must be implemented by subclasses.
        """
        raise NotImplementedError

    # ---------------------------------------------------------------------- #
    # Optional parameter validation hook
    # ---------------------------------------------------------------------- #
    def validate_params(self, params: MineParamsT) -> MineParamsT:
        """Validate extraction-specific input parameters."""
        super().validate_params(params)
        return params

    # ---------------------------------------------------------------------- #
    # Main pipeline
    # ---------------------------------------------------------------------- #
    def use(self, params: MineParamsT) -> ResultT:
        """
        Execute the full extraction pipeline.

        Steps:
            1. validate_params
            2. extract
            3. validate_result
            4. postprocess
        """
        if params is None:
            raise ValueError("Input parameters cannot be None")

        logger.debug("Starting MineStyle '%s' extraction pipeline.", self.style_name)

        try:
            # Validate parameters
            validated_params = self.validate_params(params)
            logger.debug("%s: validate_params() completed.", self.style_name)

            # Step 2: Extract
            result = self.extract(validated_params)
            logger.debug("%s: extract() completed.", self.style_name)

            # Step 3: Validate result
            result = self.validate_result(result)
            logger.debug("%s: validate_result() completed.", self.style_name)

            # Step 4: Postprocess
            result = self.postprocess(result)
            logger.debug("%s: postprocess() completed.", self.style_name)

            # Update metadata
            self.metadata.update(
                {
                    "last_extraction": datetime.now(timezone.utc),
                    "params_type": type(params).__name__,
                    "result_type": (
                        type(result).__name__ if result is not None else None
                    ),
                }
            )

            return result

        except Exception as e:
            self.log_error(e)
            raise
