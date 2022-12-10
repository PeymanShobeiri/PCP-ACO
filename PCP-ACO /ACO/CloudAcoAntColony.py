"""
from .pyisula.Ant import Ant
from .pyisula.AntColony import AntColony
from .CloudAcoAntForWorkflow import CloudAcoAntForWorkflow
from .pyisula.ConfigurationProvider import ConfigurationProvider
from .pyisula.exception.ConfigurationException import ConfigurationException
import sys

class CloudAcoAntColony(AntColony):

    def __init__(self, numberOfAnts):
        super().__init__(numberOfAnts)
        self.__solution = "NOT_FOUND"
        self.__solutionCost = sys.maxsize

    def createAnt(self, cloudAcoEnvironment):
        tmp = CloudAcoAntForWorkflow(cloudAcoEnvironment)
        return tmp
    
    def getBestPerformingAnt(self, environment):
        bestAnt = self.getHive()[0]
        var3 = self.getHive()
        bestCost = sys.maxsize
        for ant in var3:
            if ant.getLastSolutionCost() < bestCost and ant.isValidAnswer():
                bestAnt = ant
                bestCost = ant.getLastSolutionCost()
        
        return bestAnt
    
    def buildSolutions(self, environment, configurationProvider):
        if len(self.getHive()) == 0:
            raise ConfigurationException("Your colony is empty: You have no ants to solve the problem. Have you called the buildColony() method?. Number of ants from configuration provider: " + configurationProvider.getNumberOfAnts())
        else:
            for ant in self.getHive():
                failed = False

                while not ant.isSolutionReady(environment):
                    try:
                        ant.selectNextNode(environment, configurationProvider)
                    except:
                        failed = True
                        break
                
                if not failed:
                    ant.setValidAnswer(True)
                    antCost = ant.getSolutionCost(environment)

                    if self.__solutionCost > antCost and antCost != 0:
                        self.__solutionCost = antCost
                        self.__solution = ant.getSolutionAsString()
                        if ant.isValidAnswer():
                            print("valid Answer found! cost: " + self.__solutionCost)
                
                ant.doAfterSolutionIsReady(environment, configurationProvider)
            
            CloudAcoAntForWorkflow().resetCache()
    
    def getSolution(self):
        return self.__solution
    
    def getSolutionCost(self):
        return self.__solutionCost
        
"""