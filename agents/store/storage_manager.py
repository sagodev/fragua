"""
StorageManager agent for Fragua ETL.
Acts as the central interface between agents and the unified Storage.
"""

from core.base_agent import BaseAgent
from agents.store.storage import Storage
from utils.logger import get_logger


class StorageManager(BaseAgent):
    """
    StorageManager agent that interacts with Storage and provides
    a clean API for other agents (Miner, Blacksmith, Transporter).
    """

    def __init__(self, name: str = "StorageManager"):
        super().__init__(name)
        self.logger = get_logger(name)
        self.storage = Storage()

    def work(self):
        """
        StorageManager doesn't perform active work.
        This method exists to satisfy BaseAgent's abstract interface.
        """
        pass

    # -------------------
    # Wagons
    # -------------------
    def save_wagon(self, name: str, wagon):
        self.logger.info(f"Saving Wagon: {name}")
        self.storage.save_wagon(name, wagon)

    def load_wagon(self, name: str):
        return self.storage.load_wagon(name)

    def remove_wagon(self, name: str):
        return self.storage.remove_wagon(name)

    def has_wagon(self, name: str):
        return self.storage.has_wagon(name)

    # -------------------
    # Boxes
    # -------------------
    def save_box(self, name: str, box):
        self.logger.info(f"Saving Box: {name}")
        self.storage.save_box(name, box)

    def load_box(self, name: str):
        return self.storage.load_box(name)

    def remove_box(self, name: str):
        return self.storage.remove_box(name)

    def has_box(self, name: str):
        return self.storage.has_box(name)

    # -------------------
    # Containers
    # -------------------

    def save_container(self, name: str, container):
        self.logger.info(f"Saving Container: {name}")
        self.storage.save_container(name, container)

    def load_container(self, name: str):
        return self.storage.load_container(name)

    def remove_container(self, name: str):
        return self.storage.remove_container(name)

    def has_container(self, name: str):
        return self.storage.has_container(name)

    # -------------------
    # Reporting
    # -------------------
    def list_all(self):
        return {
            "wagons": list(self._wagons.keys()),
            "boxes": list(self._boxes.keys()),
            "containers": list(self._containers.keys()),
        }

    def report(self):
        return self.storage.metadata_report()
