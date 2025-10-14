"""
Containers for storing loaded data before final delivery.

Containers allow versioned storage of data that has been processed and is ready for delivery.
"""


class Container:
    """
    Represents a storage container for loaded data.
    """

    def __init__(self, name: str, data=None):
        """
        Initialize a Container with a name and optional data.

        Args:
            name (str): Name of the Container.
            data: Optional initial data.
        """
        self.name = name
        self.data = data

    def store(self, data):
        """
        Store data in the Container.

        Args:
            data: Data to store.
        """
        self.data = data

    def retrieve(self):
        """
        Retrieve data from the Container.

        Returns:
            Stored data.
        """
        return self.data

    def __repr__(self):
        return f"<Container name={self.name} data={'set' if self.data else 'empty'}>"
