"""Abstract base class for pickaxes (extractors)."""

from abc import ABC, abstractmethod
from ...storage.bagons import Bagon


class Pickaxe(ABC):
    """
    Base interface for all pickaxes.
    Implementations should return a Bagon or a pandas.DataFrame.
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def extract(self) -> Bagon:
        """
        Perform extraction and return a Bagon (or DataFrame).
        """
        raise NotImplementedError
