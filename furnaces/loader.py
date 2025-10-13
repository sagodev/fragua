from .base import FurnaceBase

class LoaderFurnace(FurnaceBase):
    def forge(self, data):
        print(f"{self.name}: Loading data...")
        print(data)
        return data
