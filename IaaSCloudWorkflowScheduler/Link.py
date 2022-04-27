class Link:
    def __init__(self, newId , newSize):
        self.id = newId
        self.dataSize = newSize

    def getDataSize(self):
        return self.dataSize
    
    def getId(self):
        return self.id