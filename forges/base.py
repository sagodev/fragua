from abc import ABC, abstractmethod

class ForgeBase(ABC):
    def __init__(self, name, forge_type):
        self.name = name
        self.type = forge_type
        self.furnaces = []

    def add_furnace(self, furnace):
        self.furnaces.append(furnace)

    @abstractmethod
    def execute(self):
        data = None
        for furnace in self.furnaces:
            data = furnace.forge(data)
        return data
