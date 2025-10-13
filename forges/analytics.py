from .base import ForgeBase

class AnalyticsForge(ForgeBase):
    def __init__(self, name="AnalyticsForge"):
        super().__init__(name, forge_type="Analytics")

    def execute(self):
        data = None
        for furnace in self.furnaces:
            data = furnace.forge(data)
        return data
