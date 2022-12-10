from ..Ant import Ant
from ..ConfigurationProvider import ConfigurationProvider
from .MaxMinConfigurationProvider import MaxMinConfigurationProvider
from ..DaemonAction import DaemonAction
from ..DaemonActionType import DaemonActionType
from ..Environment import Environment
from ..algorithms.PheromoneUtils import PheromoneUtils
from abc import ABC,abstractmethod
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)


class UpdatePheromoneMatrixForMaxMin(DaemonAction , ABC):

    def __init__(self):
        super().__init__(DaemonActionType().AFTER_ITERATION_CONSTRUCTION)
    
    def getMinimumPheromoneValue(self, configurationProvider):
        return configurationProvider.getMinimumPheromoneValue()

    def getMaximumPheromoneValue(self, configurationProvider):
        return configurationProvider.getMaximumPheromoneValue()

    @abstractmethod
    def getNewPheromoneValue(self, ant, positionInSolution, solutionComponent, configurationProvider):
        pass

    def applyDaemonAction(self, provider):
        configurationProvider = MaxMinConfigurationProvider(provider)
        logger.log(logging.DEBUG, "UPDATING PHEROMONE TRAILS")
        logger.log(logging.DEBUG,  "Performing evaporation on all edges")
        logger.log(logging.DEBUG,  "Evaporation ratio: " + configurationProvider.getEvaporationRatio())

        pheromoneMatrix = self.getEnvironment().getPheromoneMatrix()
        matrixRows = len(pheromoneMatrix)
        matrixColumns = len(pheromoneMatrix[0])

        for i in range(matrixRows):
            for j in range(matrixColumns):
                newValue = pheromoneMatrix[i][j] * configurationProvider.getEvaporationRatio()

                pheromoneMatrix[i][j] = max(newValue , self.getMinimumPheromoneValue(configurationProvider))

                PheromoneUtils.validatePheromoneValue(pheromoneMatrix[i][j])
        
        logger.log(logging.DEBUG ,  "Depositing pheromone on Best Ant trail.")
        bestAnt = self.getAntColony().getBestPerformingAnt(self.getEnvironment)
        bestSolution = bestAnt.getSolution()

        def componentIndex(index):
            solutionComponent = bestSolution[index]
            newValue = self.getNewPheromoneValue(bestAnt, index, solutionComponent, configurationProvider)
            return min(newValue, self.getMaximumPheromoneValue(configurationProvider))


        PheromoneUtils.updatePheromoneForAntSolution(bestAnt, self.getEnvironment, componentIndex)

        logger.log(logging.DEBUG ,  "After pheromone update: " + str(self.getEnvironment().getPheromoneMatrix()))

    