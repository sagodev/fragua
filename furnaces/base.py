from abc import ABC, abstractmethod

class FurnaceBase(ABC):
    def __init__(self, name, fuel=None):
        self.name = name
        self.fuel = fuel  # Configuration or parameters

    @abstractmethod
    def forge(self, data):
        """Process the data in this furnace"""
        pass
