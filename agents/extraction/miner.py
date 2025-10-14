"""
Miner agent responsible for extracting data from various sources.

The Miner uses Pickaxes to extract data and stores it in Bagons via StorageManager.
"""

from core.base_agent import BaseAgent
from agents.extraction.pickaxe import Pickaxe


class Miner(BaseAgent):
    """
    Miner agent for data extraction.
    """

    def __init__(self, name: str):
        """
        Initialize Miner with a name and empty list of pickaxes.

        Args:
            name (str): Name of the Miner.
        """
        super().__init__(name)
        self.pickaxes = []

    def add_pickaxe(self, pickaxe: Pickaxe):
        """
        Add a Pickaxe tool to the Miner.

        Args:
            pickaxe (Pickaxe): Pickaxe instance to add.
        """
        self.pickaxes.append(pickaxe)

    def work(self, storage):
        """
        Execute all pickaxes and store data in Bagons.

        Args:
            storage (StorageManager): Storage manager instance.
        """
        for pickaxe in self.pickaxes:
            data = pickaxe.use(None)  # In future, pass parameters as needed
            storage.save_wagon(f"{self.name}_{pickaxe.tool_name}", data)
