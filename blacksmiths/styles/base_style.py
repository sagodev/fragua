"""Base class for ForgeStyles."""

from abc import ABC, abstractmethod
from storage.bagons import Bagon

class ForgeStyle(ABC):
    """
    Abstract base class for all forge styles.
    """

    @abstractmethod
    def transform(self, bagon: Bagon) -> Bagon:
        """
        Transform the given Bagón and return the modified Bagón.
        """
        raise NotImplementedError
