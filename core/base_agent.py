"""
Base class for all ETL agents in Fragua.

This class defines the common interface and behavior for Miners,
Blacksmiths, and Transporters.
"""

from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """
    Abstract base class for ETL agents.
    """

    def __init__(self, name: str):
        """
        Initialize the agent with a given name.

        Args:
            name (str): The name of the agent.
        """
        self.name = name

    @abstractmethod
    def work(self, storage):
        """
        Execute the agent's main task using the provided storage.

        Args:
            storage (StorageManager): Storage manager instance.
        """
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name}>"
