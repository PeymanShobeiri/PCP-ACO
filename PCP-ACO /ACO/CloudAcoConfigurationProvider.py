

class CloudAcoConfigurationProvider:

    def getMinCost(self):
        return 50.0

    def getMaxCost(self):
        return 15000
    
    def __init__(self):
        self.antNumber = 300
        self.evaporationRatio = 0.1
        self.heuristicRatio = 0.6
        self.pheromoneRatio = 0.4
        self.iteration = 200
        self.Q0 = 0.9
        self.environment = None
        self.initialPheromone = (self.getMinCost() / self.getMaxCost()) ** 2

    def getNumberOfAnts(self):
        return self.antNumber
    
    def getEvaporationRatio(self):
        return self.evaporationRatio
    
    def getNumberOfIterations(self):
        return self.iteration
    
    def getInitialPheromoneValue(self):
        return self.initialPheromone
    
    def getHeuristicImportance(self):
        return self.heuristicRatio
    
    def getPheromoneImportance(self):
        return self.pheromoneRatio
    
    def getEnvironment(self):
        return self.environment
    
    def setEnvironment(self, environment):
        self.environment = environment
    
    def getBestChoiceProbability(self):
        return self.Q0
    
    def getMaximumPheromoneValue(self):
        raise Exception(  "We don't use this parameter in this version of the Algorithm")

    def getMinimumPheromoneValue(self):
        raise Exception( "We don't use this parameter in this version of the Algorithm")
