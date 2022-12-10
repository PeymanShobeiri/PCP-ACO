from .pyisula.ConfigurationProvider import ConfigurationProvider
from .pyisula.Environment import Environment
from .pyisula.algorithms.AcsConfigurationProvider import AcsConfigurationProvider
from .pyisula.algorithms.RandomNodeSelection import RandomNodeSelection
from .pyisula.exception.ConfigurationException import ConfigurationException
from .pyisula.exception.SolutionConstructionException import SolutionConstructionException
import random
from .CloudAcoProblemNode import CloudAcoProblemNode
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)

class CloudAcoPseudoRandomNodeSelection(RandomNodeSelection):
    
    def __init__(self):
        self.__lastMakeSpan = 0.0
        self.__lastNodeId = -1

    def selectMostConvenient(self, configurationProvider):
        Q0 = configurationProvider.getBestChoiceProbability()
        Q = random.random()
        return Q <= Q0

    def getMostConvenient(self, possibleMoves):
        nextNode = None
        currentMaximumProbability = -100000.0
        for componentWithProbability in possibleMoves:  # turn to Set ?? 
            possibleMove = list(componentWithProbability.keys())
            currentProbability = list(componentWithProbability.values())
            if not self.getAnt().isNodeVisited(possibleMove) and currentProbability > currentMaximumProbability:
                nextNode = possibleMove
                currentMaximumProbability = currentProbability
            elif not self.getAnt().isNodeVisited(possibleMove) and currentProbability == currentMaximumProbability:
                last = CloudAcoProblemNode(nextNode).getResource()
                current = CloudAcoProblemNode(possibleMove).getResource()

                if last.getInstanceRemainingTime(last.getInstanceReleaseTime() * last.getMIPS()) == (current.getInstanceRemainingTime(current.getInstanceReleaseTime()) * current.getMIPS()):
                    if last.getResource().getCost() > current.getResource().getCost():
                        nextNode = possibleMove
                elif (last.getInstanceRemainingTime(last.getInstanceReleaseTime()) * last.getMIPS()) <  (current.getInstanceRemainingTime(current.getInstanceReleaseTime()) * current.getMIPS()):
                    nextNode = possibleMove
        
        return nextNode

    def RWSSelection(self, environment, componentsWithProbabilities):
        nextNode = None
        value = random()
        total = 0.0
        iterator = iter(componentsWithProbabilities)
        componentWithProbability = {}
        while True:
            if next(iterator,None) == None:
                self.doIfNoComponentsFound(None, None)
            
            componentWithProbability = next(iterator, None)
            probability = componentsWithProbabilities[componentWithProbability]
            if probability == None:
                raise ConfigurationException("The probability for component " + componentWithProbability + " is not a number.")
            
            total += probability

            if total < value:
                break
        
        nextNode = componentWithProbability
        CloudAcoProblemNode(nextNode).setByRW = True
        CloudAcoProblemNode(nextNode).h = self.getAnt().getHeuristicValue(nextNode, self.getAnt().getCurrentIndex(), environment)
        self.getAnt().visitNode(nextNode)
        return True

    def applyPolicy(self, environment, configuration):
        nodeWasSelected = False
        configurationProvider = AcsConfigurationProvider(configuration)
        componentsWithProbabilities = self.getComponentsWithProbabilities(environment , configurationProvider)

        if self.selectMostConvenient(configurationProvider):
            logger.info("Selecting the greedy choice\n")
            nextNode = self.getMostConvenient(componentsWithProbabilities)
            if nextNode != None:
                CloudAcoProblemNode(nextNode).setByRW = False
                CloudAcoProblemNode(nextNode).h = self.getAnt().getHeuristicValue(nextNode , self.getAnt().getCurrentIndex(), environment)
                nodeWasSelected = True
                self.getAnt().visitNode(nextNode)
        else : 
            logger.info("Selecting the probabilistic choice\n")
            nodeWasSelected = self.RWSSelection(environment, componentsWithProbabilities)
            return nodeWasSelected
        
        if not nodeWasSelected:
            self.doIfNoComponentsFound(environment , configurationProvider)
        
        return True
    
    def printSolution(self,solution):
        for c in solution:
            if c != None:
                print(c)
    
    def getLastMakeSpan(self):
        return self.__lastMakeSpan
    
    def setLastMakeSpan(self, lastMakeSpan):
        self.__lastMakeSpan = lastMakeSpan
    
    def getCloudAcoHeuristicTimesPheromone(self,environment,configurationProvider,possibleMove ):
        heuristicValue = self.getAnt().getHeuristicValue(possibleMove, self.getAnt().getCurrentIndex(), environment)
        pheromoneTrailValue = self.getAnt().getPheromoneTrailValue(possibleMove, self.getAnt().getCurrentIndex(), environment)

        if heuristicValue != None and pheromoneTrailValue != None:
            return pow(heuristicValue,0.6) * pow(pheromoneTrailValue,0.4)
        
        else:
            raise SolutionConstructionException("The current ant is not producing valid pheromone/heuristic values " +
                    "for the solution component: " + possibleMove + " .Heuristic value " + heuristicValue +
                    " Pheromone value: " + pheromoneTrailValue)

    def getComponentsWithProbabilities(self,environment ,configurationProvider):
        componentsWithProbabilities = {}
        totalProbability = 0.0
        neighbourhood = self.getAnt().getNeighbourhood(environment)
        if neighbourhood == None:
            raise SolutionConstructionException("The ant's neighbourhood is null. There are no candidate components to add.")
        else:
            for possibleMove in self.getAnt().getNeighbourhood(environment):
                if not self.getAnt().isNodeVisited(possibleMove) and self.getAnt().isNodeValid(possibleMove):
                    heuristicTimesPheromone = self.getCloudAcoHeuristicTimesPheromone(environment, configurationProvider, possibleMove)
                    totalProbability += heuristicTimesPheromone
                    componentsWithProbabilities[possibleMove] = heuristicTimesPheromone
            
            # wrong path we should skip this solution
            if totalProbability ==0:
                return self.doIfNoComponentsFound(environment, configurationProvider)
            
            for key, val in componentsWithProbabilities.items():
                componentsWithProbabilities[key] = (componentsWithProbabilities[key] / totalProbability)
            
            if len(componentsWithProbabilities) < 1:
                return self.doIfNoComponentsFound(environment, configurationProvider)
            
            else:
                return componentsWithProbabilities
        
    def doIfNoComponentsFound(self, environment, configurationProvider):
        raise SolutionConstructionException("We have no suitable components to add! wrong path we should skip this solution")
        