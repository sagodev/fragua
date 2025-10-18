"""
Base DeliveryStyle class for Fragua Deliveries.
Contains common utilities for delivery workflows.
"""

from abc import abstractmethod
from typing import Any, TypeVar, Generic, Dict, Type
from datetime import datetime, timezone
from fragua.core.base_style import Style
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


def register_delivery_style(name: str):
    """
    Decorator to register a DeliveryStyle subclass.
    """

    def wrapper(cls):
        DELIVERYSTYLE_REGISTRY[name] = cls
        logger.debug("Registered DeliveryStyle: %s", name)
        return cls

    return wrapper



# Generic type variable for delivery data
T = TypeVar("T")

class DeliveryStyle(Style, Generic[T]):
    """
    Base class for all delivery styles in Fragua ETL.
    """

    def __init__(self, style_name: str):
        super().__init__(style_name)
        self.destination = None
        self.created_at = datetime.now(timezone.utc)

    @abstractmethod
    def deliver(self, data: T) -> T:
        """
        Deliver the given data to the target destination.
        Must be implemented by subclasses.
        """
        pass

    def validate(self, data: T) -> T:
        """
        Extend basic validation for delivery-specific requirements.

        Args:
            data: Data to be validated before delivery.

        Returns:
            The validated data.
        """
        data = super().validate(data)
        if self.destination is None:
            raise ValueError(
                f"{self.style_name} requires a destination to deliver data."
            )
        return data

    def use(self, data: Any) -> Any:
        """
        Main Delivery method.
        Executes forge -> validate -> postprocess pipeline.
        """
        if data is None:
            raise ValueError("Input data cannot be None")

        logger.debug("Starting DeliveryStyle '%s' loading pipeline.", self.style_name)

        try:
            data = self.deliver(data)
            logger.debug("%s: deliver() step completed.", self.style_name)

            data = self.validate(data)
            logger.debug("%s: validate() step completed.", self.style_name)

            data = self.postprocess(data)
            logger.debug("%s: postprocess() step completed.", self.style_name)

            return data

        except Exception as e:
            self.log_error(e)
            raise


# Registry for dynamic DeliveryStyle discovery
DELIVERYSTYLE_REGISTRY: Dict[str, Type[DeliveryStyle[Any]]] = {}
