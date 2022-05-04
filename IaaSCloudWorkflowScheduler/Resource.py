class Resource:
    def __init__(self, newId, cost=0, mips=0):
        self.id = newId
        self.costPerInterval = cost
        self.MIPS = mips

    def __gt__(self, other):  # this or function
        return self.MIPS > other.MIPS

    def getId(self):
        return self.id

    def getCost(self):
        return self.costPerInterval

    def setCost(self, newCost):
        if newCost >= 0:
            self.costPerInterval = newCost

    def getMIPS(self):
        return self.MIPS
