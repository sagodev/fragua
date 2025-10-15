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
    Now automatically saves delivered data in Containers.
    """

    def __init__(self, name: str):
        super().__init__(name)
        # Each cart stored as tuple: (Cart instance, delivery parameters)
        self.carts = []

    def add_cart(self, cart: Cart, delivery_params: dict):
        """
        Add a Cart tool to the Transporter with delivery parameters.
        """
        self.carts.append((cart, delivery_params))

    def work(self, storage: StorageManager):
        """
        Deliver data from Boxes to final destinations using carts.
        Automatically stores delivered data in Containers.
        """
        for cart, params in self.carts:
            # Retrieve data from Box
            box_name = f"{self.name}_{cart.__class__.__name__}"
            input_data = storage.load_box(box_name)

            if input_data is None:
                print(
                    f"No data found in box '{box_name}' for cart '{cart.__class__.__name__}'"
                )
                continue

            # Pass StorageManager and container_name to the Cart
            cart.deliver(input_data, storage=storage, container_name=box_name, **params)
