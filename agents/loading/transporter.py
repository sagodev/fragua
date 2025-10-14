"""
Transporter agent responsible for loading data to final destinations.
The Transporter uses Carts to deliver data from Boxes to databases, files, or APIs.
"""

from core.base_agent import BaseAgent
from core.storage_manager import StorageManager
from agents.loading.cart import Cart


class Transporter(BaseAgent):
    """
    Transporter agent for loading data.
    """

    def __init__(self, name: str):
        """
        Initialize Transporter with a name and empty list of carts.

        Args:
            name (str): Name of the Transporter.
        """
        super().__init__(name)
        # Each cart will be stored as a tuple: (Cart instance, delivery parameters)
        self.carts = []

    def add_cart(self, cart: Cart, delivery_params: dict):
        """
        Add a Cart tool to the Transporter with delivery parameters.

        Args:
            cart (Cart): Cart instance to add.
            delivery_params (dict): Dictionary with arguments for deliver().
        """
        self.carts.append((cart, delivery_params))

    def work(self, storage: StorageManager):
        """
        Deliver data from Boxes to final destinations using carts.

        Args:
            storage (StorageManager): Storage manager instance.
        """
        for cart, params in self.carts:
            # Retrieve data from Box
            box_name = f"{self.name}_{cart.__class__.__name__}"
            input_data = storage.load_box(box_name)

            # Deliver data using the unified deliver() method
            cart.deliver(input_data, **params)

            # Store delivered data in Container for versioning
            storage.save_container(box_name, input_data)
