"""
Transporter agent responsible for loading data to final destinations.

The Transporter uses Carts to deliver data from Boxes to databases, files, or APIs.
"""

from core.base_agent import BaseAgent
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
        self.carts = []

    def add_cart(self, cart: Cart):
        """
        Add a Cart tool to the Transporter.

        Args:
            cart (Cart): Cart instance to add.
        """
        self.carts.append(cart)

    def work(self, storage):
        """
        Deliver data from Boxes to final destinations using carts.

        Args:
            storage (StorageManager): Storage manager instance.
        """
        for cart in self.carts:
            # Retrieve data from Box
            input_data = storage.load_box(f"{self.name}_{cart.tool_name}")
            # Deliver data
            cart.use(input_data)
            # Store delivered data in Container
            storage.save_container(f"{self.name}_{cart.tool_name}", input_data)
