from forges.analytics import AnalyticsForge
from furnaces.extractor import ExtractorFurnace
from furnaces.transformer import TransformerFurnace
from furnaces.loader import LoaderFurnace
from smiths.smith import Smith


class Fragua:
    def __init__(self):
        self.forges = {}

    def add_forge(self, forge):
        self.forges[forge.name] = forge

    def execute_forge(self, name):
        forge = self.forges.get(name)
        if not forge:
            raise ValueError(f"Forge {name} not found")
        return forge.execute()


# Example usage
if __name__ == "__main__":
    # Create a forge
    analytics = AnalyticsForge()
    analytics.add_furnace(ExtractorFurnace("Extractor1"))
    analytics.add_furnace(TransformerFurnace("Transformer1"))
    analytics.add_furnace(LoaderFurnace("Loader1"))

    # Create smith and assign forge
    smith = Smith("John", specialization="Analytics")
    smith.assign_forge(analytics)

    # Execute
    results = smith.execute_forges()
