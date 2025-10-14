"""
Base class for all carts used by Transporters in Fragua.
Defines the interface for delivering data.
"""

from abc import ABC, abstractmethod


class Cart(ABC):
    """Abstract base class for delivery carts."""

    @abstractmethod
    def deliver(self, *args, **kwargs):
        """
        Deliver data to the cart's destination.
        Must be implemented by all subclasses.

        Parameters:
        - *args, **kwargs: Subclass-specific arguments.
        """
        pass
