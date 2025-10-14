"""
Blacksmith agent responsible for transforming data.

The Blacksmith uses ForgeStyles to process data from Wagons and stores results in Boxes.
"""

from core.base_agent import BaseAgent
from agents.transformation.forge_style import ForgeStyle


class Blacksmith(BaseAgent):
    """
    Blacksmith agent for data transformation.
    """

    def __init__(self, name: str):
        """
        Initialize Blacksmith with a name and empty list of forge styles.

        Args:
            name (str): Name of the Blacksmith.
        """
        super().__init__(name)
        self.forge_styles = []

    def add_forge_style(self, forge_style: ForgeStyle):
        """
        Add a ForgeStyle tool to the Blacksmith.

        Args:
            forge_style (ForgeStyle): ForgeStyle instance to add.
        """
        self.forge_styles.append(forge_style)

    def work(self, storage):
        """
        Apply all forge styles to data from Wagons and store in Boxes.

        Args:
            storage (StorageManager): Storage manager instance.
        """
        for forge_style in self.forge_styles:
            # Retrieve data from Wagon
            input_data = storage.load_wagon(f"{self.name}_{forge_style.tool_name}")
            # Apply transformation
            transformed = forge_style.use(input_data)
            # Store transformed data in Box
            storage.save_box(f"{self.name}_{forge_style.tool_name}", transformed)
