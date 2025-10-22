"""
Base DeliveryStyle class for Fragua Deliveries.
Contains common utilities for delivery workflows.
"""

from abc import abstractmethod
from typing import Type, Callable, Dict, Any, Generic
from datetime import datetime, timezone
from fragua.core.base_style import BaseStyle, ResultT
from fragua.params.delivery_params import DeliveryParamsT
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------- #
# Type Variables
# ---------------------------------------------------------------------- #

# Registry for dynamic loading
DELIVERYSTYLE_REGISTRY: Dict[str, Type["DeliveryStyle[Any,Any]"]] = {}


def register_delivery_style(
    name: str,
) -> Callable[[Type["DeliveryStyle[Any,Any]"]], Type["DeliveryStyle[Any,Any]"]]:
    """
    Decorator to register a DeliveryStyle subclass.
    """

    def wrapper(cls: Type["DeliveryStyle[Any,Any]"]) -> Type["DeliveryStyle[Any,Any]"]:
        DELIVERYSTYLE_REGISTRY[name] = cls
        logger.debug("Registered DeliveryStyle: %s", name)
        return cls

    return wrapper


# ---------------------------------------------------------------------- #
# DeliveryStyle Base
# ---------------------------------------------------------------------- #
class DeliveryStyle(
    BaseStyle[DeliveryParamsT, ResultT], Generic[DeliveryParamsT, ResultT]
):
    """
    Base class for all delivery styles in Fragua ETL.

    Provides the standardized pipeline:
        validate_params -> deliver -> validate_result -> postprocess
    """

    def __init__(self, style_name: str):
        super().__init__(style_name)
        self.created_at: datetime = datetime.now(timezone.utc)

    # ---------------------------------------------------------------------- #
    # Abstract delivery method
    # ---------------------------------------------------------------------- #
    @abstractmethod
    def deliver(self, params: DeliveryParamsT) -> ResultT:
        """Deliver the given data to the target destination. Must be overridden."""
        raise NotImplementedError("Subclasses must implement deliver()")

    # ---------------------------------------------------------------------- #
    # Validation hooks
    # ---------------------------------------------------------------------- #
    def validate_params(self, params: DeliveryParamsT) -> DeliveryParamsT:
        """Validate delivery-specific input parameters."""
        super().validate_params(params)

        if not getattr(params, "destination", None):
            raise ValueError(f"{self.style_name}: 'destination' is required.")

        return params

    # ---------------------------------------------------------------------- #
    # Main pipeline
    # ---------------------------------------------------------------------- #
    def use(self, params: DeliveryParamsT) -> ResultT:
        """
        Execute the full delivery pipeline.

        Steps:
            1. validate_params
            2. deliver
            3. validate_result
            4. postprocess
        """
        if params is None:
            raise ValueError("Input delivery parameters cannot be None")

        logger.debug("Starting DeliveryStyle '%s' pipeline.", self.style_name)

        try:
            # Validate parameters
            validated = self.validate_params(params)
            logger.debug("%s: validate_params() completed.", self.style_name)

            # Deliver
            result = self.deliver(validated)
            logger.debug("%s: deliver() completed.", self.style_name)

            # Validate result
            result = self.validate_result(result)
            logger.debug("%s: validate_result() completed.", self.style_name)

            # Postprocess
            result = self.postprocess(result)
            logger.debug("%s: postprocess() completed.", self.style_name)

        except Exception as e:
            self.log_error(e)
            raise

        return result
