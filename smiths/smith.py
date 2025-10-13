class Smith:
    def __init__(self, name, specialization=None):
        self.name = name
        self.specialization = specialization
        self.forges = []

    def assign_forge(self, forge):
        if self.specialization and forge.type != self.specialization:
            raise ValueError(f"{self.name} cannot handle forge type {forge.type}")
        self.forges.append(forge)

    def execute_forges(self):
        results = {}
        for forge in self.forges:
            results[forge.name] = forge.execute()
        return results
