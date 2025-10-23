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
# Registry for dynamic loading
# ---------------------------------------------------------------------- #
DELIVERYSTYLE_REGISTRY: Dict[str, Type["DeliveryStyle[Any, Any]"]] = {}


def register_delivery_style(
    name: str,
) -> Callable[[Type["DeliveryStyle[Any, Any]"]], Type["DeliveryStyle[Any, Any]"]]:
    """
    Decorator to register a DeliveryStyle subclass.
    """

    def wrapper(
        cls: Type["DeliveryStyle[Any, Any]"],
    ) -> Type["DeliveryStyle[Any, Any]"]:
        DELIVERYSTYLE_REGISTRY[name] = cls
        logger.debug("Registered DeliveryStyle: %s", name)
        return cls

    return wrapper


# ---------------------------------------------------------------------- #
# Base DeliveryStyle
# ---------------------------------------------------------------------- #
class DeliveryStyle(
    BaseStyle[DeliveryParamsT, ResultT], Generic[DeliveryParamsT, ResultT]
):
    """
    Base class for all delivery styles in Fragua ETL.

    Standard pipeline provided by BaseStyle:
        validate_params -> _run -> validate_result -> postprocess
    """

    # ---------------------------------------------------------------------- #
    # Abstract delivery method
    # ---------------------------------------------------------------------- #
    @abstractmethod
    def deliver(self, params: DeliveryParamsT) -> ResultT:
        """
        Deliver the given data to the target destination.
        Must be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement deliver()")

    # ---------------------------------------------------------------------- #
    # Optional parameter validation hook
    # ---------------------------------------------------------------------- #
    def validate_params(self, params: DeliveryParamsT) -> DeliveryParamsT:
        """Validate delivery-specific input parameters."""
        super().validate_params(params)

        if not getattr(params, "destination", None):
            raise ValueError(f"{self.style_name}: 'destination' is required.")

        return params

    # ---------------------------------------------------------------------- #
    # Internal _run implementation for BaseStyle
    # ---------------------------------------------------------------------- #
    def _run(self, params: DeliveryParamsT) -> ResultT:
        """
        Executes the DeliveryStyle delivery step.

        This method is called by BaseStyle.use().
        """
        logger.debug("Starting DeliveryStyle '%s' delivery.", self.style_name)
        result = self.deliver(params)
        logger.debug("DeliveryStyle '%s' delivery completed.", self.style_name)
        return result
