from ..Ant import Ant
from ..Environment import Environment
from ..exception.ConfigurationException import ConfigurationException
import sys

class PheromoneUtils:

    def validatePheromoneValue(self, v):
        if v == sys.maxsize or v == None:
            raise ConfigurationException("The pheromone value calculated is not a valid number: " + v)
    
    def updatePheromoneForAntSolution(self, ant, environment, pheromoneUpdater):

        antSolution =  ant.getSolution()

        for componentIndex in range(len(antSolution)):
            solutionComponent = antSolution[componentIndex]
            newValue = pheromoneUpdater(componentIndex)

            if newValue != None:
                ant.setPheromoneTrailValue(solutionComponent, componentIndex, environment, newValue)
                self.validatePheromoneValue(ant.getPheromoneTrailValue(solutionComponent, componentIndex, environment))