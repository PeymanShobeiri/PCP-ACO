
from random import choices
from math import isnan
from ..exception.ConfigurationException import ConfigurationException
from ..AntPolicy import AntPolicy
from ..AntPolicyType import AntPolicyType
from ..exception.SolutionConstructionException import SolutionConstructionException
import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)

class RandomNodeSelection(AntPolicy):
    def __init__(self):
        super().__init__(AntPolicyType.NODE_SELECTION)

    def getHeuristicTimesPheromone(self, environment, configurationProvider, possibleMove):
        heuristicValue = self.getAnt().getHeuristicValue(possibleMove, self.getAnt().getCurrentIndex(), environment)
        pheromoneTrailValue = self.getAnt().getPheromoneTrailValue(possibleMove, self.getAnt().getCurrentIndex(),environment)

        if heuristicValue == None or isnan(heuristicValue)  or heuristicValue == sys.maxsize or pheromoneTrailValue == None or isnan(pheromoneTrailValue) or pheromoneTrailValue == sys.maxsize:
            raise SolutionConstructionException("The current ant is not producing valid pheromone/heuristic values" +\
                    " for the solution component: " + possibleMove + " . Heuristic value " + heuristicValue +\
                    " Pheromone value: " + pheromoneTrailValue)
        
        return pow(heuristicValue, configurationProvider.getHeuristicImportance()) * pow(pheromoneTrailValue , configurationProvider.getPheromoneImportance())

    def doIfNoComponentsFound(self, environment , configurationProvider) :
        raise SolutionConstructionException( "We have no suitable components to add to the solution from current position."\
                        + "\n Partial solution: "\
                        + self.getAnt().getSolution()\
                        + " at position " + (self.getAnt().getCurrentIndex() - 1)\
                        + "\n Environment: " + environment.toString()\
                        + "\nPartial solution : " + self.getAnt().getSolutionAsString())

    def getProbabilitiesForNeighbourhood(self, environment, configurationProvider, neighborhood):
        componentsWithProbabilities = {}
        for k in neighborhood:
            if not self.getAnt().isNodeVisited(k) and self.getAnt().isNodeValid(k):
                componentsWithProbabilities[k] = self.getHeuristicTimesPheromone(environment, configurationProvider, k)
        
        if len(componentsWithProbabilities) < 1 :
            return self.doIfNoComponentsFound(environment , configurationProvider)

        sumOfMapValues = 0.0
        for value in componentsWithProbabilities.keys():
            sumOfMapValues += value 
        
        for key,value in componentsWithProbabilities:
            probabilityValue = value / sumOfMapValues
            if probabilityValue == None or probabilityValue == sys.maxsize:
                raise ConfigurationException("The probability for component " + key +" is not a valid number. Current value: " + probabilityValue + " (" + value + "/" + sumOfMapValues + ")")
            
            componentsWithProbabilities[key] = probabilityValue
        
        totalProbability = 0.0
        for value in componentsWithProbabilities.values():
            totalProbability += value
        
        delta = 0.001
        if abs(totalProbability - 1.0) > delta:
            raise ConfigurationException("The sum of probabilities for the possible components is " + totalProbability + ". We expect this value to be closer to 1.")
        
        return componentsWithProbabilities
                
                            
            

    def getComponentsWithProbabilities(self, environment, configurationProvider):
        neighborhood = self.getAnt().getNeighbourhood(environment)
        if neighborhood == None:
            raise SolutionConstructionException("The ant's neighbourhood is null. There are no candidate components to add.")
        
        return self.getProbabilitiesForNeighbourhood(environment , configurationProvider , neighborhood)

    def getNextComponent(self, componentsWithProbabilities):
        listOfComponents = list(componentsWithProbabilities.keys())
        probabilities = []
        for i in listOfComponents:
            probabilities.append(componentsWithProbabilities[i])
        
        componentIndexes = [i for i in range(len(listOfComponents))]
        arrayOfProbabilities = [p for p in probabilities]

        distribution = choices(componentIndexes, arrayOfProbabilities)

        return listOfComponents[distribution]


    def applyPolicy(self, environment, configurationProvider):
        logger.info("Starting node selection")
        componentsWithProbabilities = self.getComponentsWithProbabilities(environment , configurationProvider)

        nextNode = self.getNextComponent(componentsWithProbabilities)
        self.getAnt().visitNode(nextNode, environment)
        logger.info("Ending node selection")
        return True
    
    def __str__(self):
        return "RandomNodeSelection{}"
