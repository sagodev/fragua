import pandas as pd
from .base import FurnaceBase

class ExtractorFurnace(FurnaceBase):
    def forge(self, data=None):
        print(f"{self.name}: Extracting data...")
        df = pd.DataFrame({'a': [1,2,3], 'b': [4,5,6]})
        return df
