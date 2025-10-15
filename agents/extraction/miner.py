"""
Miner agent responsible for extracting data from various sources.

The Miner uses Pickaxes to extract data and stores it in Wagons via StorageManager.
"""

from core.base_agent import BaseAgent
from agents.extraction.pickaxe import Pickaxe


class Miner(BaseAgent):
    """
    Miner agent for data extraction.
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.pickaxes = []

    def add_pickaxe(self, pickaxe: Pickaxe):
        """
        Add a Pickaxe tool to the Miner.
        """
        self.pickaxes.append(pickaxe)

    def work(self, storage_manager):
        """
        Execute all pickaxes and store data in Wagons using StorageManager.
        """
        for pickaxe in self.pickaxes:
            data = pickaxe.use(None)
            wagon_name = f"{self.name}_{pickaxe.tool_name}"
            storage_manager.save_wagon(wagon_name, data)
            print(f"[Miner] Saved Wagon '{wagon_name}'")
