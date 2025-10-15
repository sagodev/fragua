"""
Blacksmith agent responsible for transforming data.

The Blacksmith uses ForgeStyles to process data from Wagons and stores results in Boxes.
"""

from core.base_agent import BaseAgent
from agents.transformation.forge_style import ForgeStyle, FORGESTYLE_REGISTRY


class Blacksmith(BaseAgent):
    """
    Blacksmith agent for transforming data.

    The Blacksmith uses ForgeStyles to process data from Wagons
    and stores results in Boxes.
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.forge_styles = []

    def add_forge_style(self, forge_style: ForgeStyle):
        """
        Add a ForgeStyle instance to the Blacksmith.

        Args:
            forge_style (ForgeStyle): ForgeStyle instance to add.
        """
        self.forge_styles.append(forge_style)

    def add_forge_style_by_name(self, name: str, **kwargs):
        """
        Add a ForgeStyle dynamically from the registry using its name.

        Args:
            name (str): Registered name of the ForgeStyle.
            **kwargs: Parameters to pass to the ForgeStyle constructor.

        Raises:
            ValueError: If no ForgeStyle is registered under the given name.
        """
        if name not in FORGESTYLE_REGISTRY:
            raise ValueError(f"No ForgeStyle registered under name '{name}'")
        forge_cls = FORGESTYLE_REGISTRY[name]
        instance = forge_cls(**kwargs) if kwargs else forge_cls(name)
        self.forge_styles.append(instance)

    def work(self, storage):
        """
        Apply all forge styles to data from Wagons and store results in Boxes.

        This method performs robust validations:
        - Checks that the Wagon exists before transformation.
        - Ensures the ForgeStyle returns a valid Box.
        - Raises informative errors if any validation fails.

        Args:
            storage (StorageManager): Storage manager instance.

        Raises:
            ValueError: If the Wagon does not exist or ForgeStyle returns None.
            TypeError: If the returned object is not a Box instance.
        """
        from agents.transformation.boxes import Box

        for forge_style in self.forge_styles:
            wagon_name = f"{self.name}_{forge_style.tool_name}"

            # 1️⃣ Validation: Wagon exists
            input_data = storage.load_wagon(wagon_name)
            if input_data is None:
                raise ValueError(
                    f"[Blacksmith ERROR] No Wagon found with name '{wagon_name}'"
                )

            # 2️⃣ Apply transformation
            transformed = forge_style.use(input_data)

            # 3️⃣ Validation: Result is not None
            if transformed is None:
                raise ValueError(
                    f"[Blacksmith ERROR] ForgeStyle '{forge_style.tool_name}' returned None"
                )

            # 4️⃣ Validation: Result is a Box
            if not isinstance(transformed, Box):
                raise TypeError(
                    f"[Blacksmith ERROR] ForgeStyle '{forge_style.tool_name}' must return a Box instance, "
                    f"got {type(transformed).__name__}"
                )

            # 5️⃣ Store in Boxes
            storage.save_box(wagon_name, transformed)
            print(f"[Blacksmith INFO] Stored transformed data in Box '{wagon_name}'")
