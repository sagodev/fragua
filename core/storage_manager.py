"""
Central storage interface for Fragua ETL agents.

This class manages Wagons, Boxes, and Containers for versioned data storage.
"""


class StorageManager:
    """
    Storage manager to handle intermediate and final data storage.
    """

    def __init__(self):
        """
        Initialize empty storage containers.
        """
        self.wagons = {}
        self.boxes = {}
        self.containers = {}

    # Wagons (extraction)
    def save_wagon(self, name: str, data):
        """
        Save data to a Wagon.

        Args:
            name (str): Name identifier for the Wagon.
            data: Data to store.
        """
        self.wagons[name] = data

    def load_wagon(self, name: str):
        """
        Load data from a Wagon.

        Args:
            name (str): Name identifier for the Wagon.

        Returns:
            Stored data.
        """
        return self.wagons.get(name, None)

    # Boxes (transformation)
    def save_box(self, name: str, data):
        """
        Save data to a Box.

        Args:
            name (str): Name identifier for the Box.
            data: Data to store.
        """
        self.boxes[name] = data

    def load_box(self, name: str):
        """
        Load data from a Box.

        Args:
            name (str): Name identifier for the Box.

        Returns:
            Stored data.
        """
        return self.boxes.get(name, None)

    # Containers (loading)
    def save_container(self, name: str, data):
        """
        Save data to a Container.

        Args:
            name (str): Name identifier for the Container.
            data: Data to store.
        """
        self.containers[name] = data

    def load_container(self, name: str):
        """
        Load data from a Container.

        Args:
            name (str): Name identifier for the Container.

        Returns:
            Stored data.
        """
        return self.containers.get(name, None)
