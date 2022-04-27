import Resource

class ResourceSet:
    def __init__(self, interval):
        self.resources = []
        self.timeInterval = interval
        self.size = None
        self.maxCost = None
        self.minCost = None
        self.maxMIPS = None
        self.meanMIPS= None
        self.minMIPS = None
    

    def getMaxMIPS(self):
        return self.maxMIPS
    
    def getMinMIPS(self):
        return self.minMIPS

    def getMeanMIPS(self):
        return self.meanMIPS
    
    def getMaxCost(self):
        return self.maxCost
    
    def getMinCost(self):
        return self.minCost
    
    def getSize(self):
        return self.size
    
    def getInterval(self):
        return self.timeInterval
    
    def addResource(self,Res):
        res = Resource(Res)
        self.resources.append(res)
        self.size += 1
    
    def getResource(self,index):
        if index < self.size:
            return self.resources[index]
        else:
            return None
    
    def getMinResource(self):
        return self.resources[self.size - 1]
    
    def getMinId(self):
        return self.size-1

    def getMaxResource(self):
        return self.resources[0]

    def getMaxId(self):
        return 0

    def sort(self):
        self.resources=sorted(self.resources)
        self.maxMIPS = self.resources[0].getMIPS()
        self.maxCost = self.resources[0].getCost() 
        self.minMIPS = self.resources[self.size-1].getMIPS()
        self.minCost = self.resources[self.size-1].getCost()

        self.meanMIPS = 0
        for res in self.resources: 
            self.meanMIPS += res.getMIPS()
        self.meanMIPS /= self.size
    
    def computeParameters(self):
        self.maxMIPS = self.resources[0].getMIPS()
        self.maxCost = self.resources[0].getCost() 
        self.minMIPS = self.resources[self.size-1].getMIPS()
        self.minCost = self.resources[self.size-1].getCost()

        self.meanMIPS = 0
        for res in self.resources: 
            self.meanMIPS += res.getMIPS()
        self.meanMIPS /= self.size