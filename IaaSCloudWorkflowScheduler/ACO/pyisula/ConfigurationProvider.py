import zope.interface

class ConfigurationProvider(zope.interface.Interface):
    def getNumberOfAnts(self):
        pass

    def getEvaporationRatio(self):
        pass

    def getNumberOfIterations(self):
        pass

    def getInitialPheromoneValue(self):
        pass

    def getHeuristicImportance(self):
        pass

    def getPheromoneImportance(self):
        pass