from .base import FurnaceBase

class TransformerFurnace(FurnaceBase):
    def forge(self, data):
        print(f"{self.name}: Transforming data...")
        data['sum'] = data['a'] + data['b']
        return data
