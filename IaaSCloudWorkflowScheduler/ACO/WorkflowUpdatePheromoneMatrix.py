"""

from IaaSCloudWorkflowScheduler.ACO.CloudAcoConfigurationProvider import CloudAcoConfigurationProvider
from .pyisula.Ant import Ant
from .pyisula.ConfigurationProvider import ConfigurationProvider
from .pyisula.algorithms.MaxMinConfigurationProvider import MaxMinConfigurationProvider
from .pyisula.algorithms.UpdatePheromoneMatrixForMaxMin import UpdatePheromoneMatrixForMaxMin
from .pyisula.exception.ConfigurationException import ConfigurationException
from .CloudAcoAntForWorkflow import CloudAcoAntForWorkflow
import sys

class WorkflowUpdatePheromoneMatrix(UpdatePheromoneMatrixForMaxMin):

    def getNewPheromoneValue(self, ant , pre , next , configurationProvider):
        cost = CloudAcoAntForWorkflow(ant).getLastSolutionCost()
        makeSpan = CloudAcoAntForWorkflow(ant).getLastMakeSpan()
        deadline = self.getEnvironment().getProblemGraph().getDeadline()
        minCost = CloudAcoConfigurationProvider(configurationProvider).getMinCost()
        maxCost = CloudAcoConfigurationProvider(configurationProvider).getMaxCost()

        k = 0.0

        if makeSpan > deadline:
            k = (deadline / makeSpan) + (minCost / maxCost)
        else:
            k = 1 + (minCost / cost)
        
        return 0.9 * ant.getPheromoneTrailValue(next, pre, self.getEnvironment()) + 0.1 * k

    
    def getMaximumPheromoneValue(self, configurationProvider):
        return 1

    def getMinimumPheromoneValue(self, configurationProvider):
        return 0.0001
    
    def validatePheromoneValue(self, v):
        if v == sys.maxsize or v == None:
            raise ConfigurationException("The pheromone value calculated is not a valid number: " + v)

    def applyDaemonAction(self, provider):
        configurationProvider = MaxMinConfigurationProvider(provider)
        pheromoneMatrix = self.getEnvironment().getPheromoneMatrix()

        matrixRows = len(pheromoneMatrix)
        matrixColumns = len(pheromoneMatrix[0])
        t0 = configurationProvider.getEvaporationRatio() * configurationProvider.getInitialPheromoneValue()

        for i in range(matrixRows):
            for j in range(matrixColumns):
                newValue = pheromoneMatrix[i][j] * configurationProvider.getEvaporationRatio()
                if newValue >= self.getMinimumPheromoneValue(configurationProvider):
                    pheromoneMatrix[i][j] = newValue
                else:
                    pheromoneMatrix[i][j] = self.getMinimumPheromoneValue(configurationProvider)
                
                self.validatePheromoneValue(pheromoneMatrix[i][j])
        
        bestAnt = self.getAntColony().getBestPerformingAnt(self.getEnvironment())
        bestSolution = bestAnt.getSolution()

        # assigning the pheromon of best solution
        componentIndex = 1
        while componentIndex < len(bestSolution):
            solutionComponent = bestSolution[componentIndex]
            lastPos = bestSolution[componentIndex - 1]
            newValue = self.getNewPheromoneValue(bestAnt, lastPos.getId() , solutionComponent, configurationProvider)
            if newValue <= self.getMaximumPheromoneValue(configurationProvider):
                bestAnt.setPheromoneTrailValue(lastPos, solutionComponent.getId() , self.getEnvironment(), newValue)
            else:
                bestAnt.setPheromoneTrailValue(lastPos, solutionComponent.getId(), self.getEnvironment(),self.getMaximumPheromoneValue(configurationProvider))
            
            self.validatePheromoneValue(bestAnt.getPheromoneTrailValue(lastPos, solutionComponent.getId(), self.getEnvironment()))
            componentIndex += 1 

"""