"""
Base DeliveryStyle class for Fragua Deliveries.
Contains common utilities for delivery workflows.
"""

from abc import abstractmethod
from typing import Generic, Type, Callable, Dict
from datetime import datetime, timezone
from fragua.core.base_style import BaseStyle, DataT, ResultT
from fragua.utils.logger import get_logger

logger = get_logger(__name__)

DELIVERYSTYLE_REGISTRY: Dict[str, Type["DeliveryStyle[DataT, ResultT]"]] = {}


def register_delivery_style(
    name: str,
) -> Callable[
    [Type["DeliveryStyle[DataT, ResultT]"]], Type["DeliveryStyle[DataT, ResultT]"]
]:
    """
    Decorator to register a DeliveryStyle subclass.
    """

    def wrapper(
        cls: Type["DeliveryStyle[DataT, ResultT]"],
    ) -> Type["DeliveryStyle[DataT, ResultT]"]:
        DELIVERYSTYLE_REGISTRY[name] = cls
        logger.debug("Registered DeliveryStyle: %s", name)
        return cls

    return wrapper


class DeliveryStyle(BaseStyle[DataT, ResultT], Generic[DataT, ResultT]):
    """
    Base class for all delivery styles in Fragua ETL.
    Provides the pipeline: deliver -> validate -> postprocess.
    """

    def __init__(self, style_name: str):
        super().__init__(style_name)
        self.destination = None
        self.created_at = datetime.now(timezone.utc)

    @abstractmethod
    def deliver(self, source_params: DataT) -> ResultT:
        """
        Deliver the given data to the target destination.
        Must be implemented by subclasses.
        """

    def validate(self, data: ResultT) -> ResultT:
        """
        Extend basic validation for delivery-specific requirements.
        """
        data = super().validate(data)
        if self.destination is None:
            raise ValueError(
                f"{self.style_name} requires a destination to deliver data."
            )
        return data

    def use(self, source_params: DataT) -> ResultT:
        """
        Main Delivery method.
        Executes deliver -> validate -> postprocess pipeline.
        """
        if source_params is None:
            raise ValueError("Input source_params cannot be None")

        logger.debug("Starting DeliveryStyle '%s' loading pipeline.", self.style_name)

        try:
            data: ResultT = self.deliver(source_params)
            logger.debug("%s: deliver() step completed.", self.style_name)

            data = self.validate(data)
            logger.debug("%s: validate() step completed.", self.style_name)

            data = self.postprocess(data)
            logger.debug("%s: postprocess() step completed.", self.style_name)

            return data

        except Exception as e:
            self.log_error(e)
            raise
