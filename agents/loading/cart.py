"""
Base class for all carts used by Transporters in Fragua.
Defines the interface for delivering data.
"""

from abc import ABC, abstractmethod
from typing import Type, Dict, Optional
from core.storage_manager import StorageManager

CART_REGISTRY: Dict[str, Type["Cart"]] = {}


def register_cart(name: str):
    """Decorator to register Cart subclasses dynamically."""

    def wrapper(cls):
        CART_REGISTRY[name] = cls
        return cls

    return wrapper


class Cart(ABC):
    """Abstract base class for delivery carts."""

    @abstractmethod
    def deliver(
        self,
        data,
        storage: Optional[StorageManager] = None,
        container_name: Optional[str] = None,
        *args,
        **kwargs
    ):
        """
        Deliver data to the cart's destination.

        Parameters:
        - data: Data to deliver
        - storage: Optional StorageManager to save data in a Container
        - container_name: Optional name for the Container
        - *args, **kwargs: Subclass-specific arguments
        """
        pass
