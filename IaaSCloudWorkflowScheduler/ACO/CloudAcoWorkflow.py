"""
import sys
sys.path.append('/Users/apple/Desktop/Create WS-ACO/MyCode')

from ..ResourceSet import ResourceSet
from ..WorkflowGraph import WorkflowGraph
from IaaSCloudWorkflowScheduler.ACO.pyisula.algorithms.StartPheromoneMatrix import StartPheromoneMatrix
from IaaSCloudWorkflowScheduler.ACO.pyisula.exception.InvalidInputException import InvalidInputException
from IaaSCloudWorkflowScheduler.ACO.pyisula.exception.ConfigurationException import ConfigurationException
from IaaSCloudWorkflowScheduler.ACO.CloudAcoProblemRepresentation import CloudAcoProblemRepresentation
from IaaSCloudWorkflowScheduler.ACO.CloudAcoConfigurationProvider import CloudAcoConfigurationProvider
from IaaSCloudWorkflowScheduler.ACO.CloudAcoProblemSolver import CloudAcoProblemSolver
from IaaSCloudWorkflowScheduler.ACO.CloudAcoEnvironment import CloudAcoEnvironment
from .CloudAcoAntColony import CloudAcoAntColony
#from IaaSCloudWorkflowScheduler.ACO.CloudAcoAntColony import CloudAcoAntColony
from IaaSCloudWorkflowScheduler.ACO.WorkflowUpdatePheromoneMatrix import WorkflowUpdatePheromoneMatrix
from IaaSCloudWorkflowScheduler.ACO.CloudAcoPseudoRandomNodeSelection import CloudAcoPseudoRandomNodeSelection


class CloudAcoWorkflow:
    antId = 0 
    def getAntColony(self, configurationProvider):
        tmp = CloudAcoAntColony(configurationProvider.getNumberOfAnts())
        return tmp

    def __init__(self, graph, resourceSet, bandwidth, deadline):
        self.__problemRepresentation = CloudAcoProblemRepresentation(graph, resourceSet, bandwidth, deadline, 10)
        self.configurationProvider = CloudAcoConfigurationProvider()
        self.__colony = self.getAntColony(self.configurationProvider)
        self.__environment = CloudAcoEnvironment(self.__problemRepresentation)
        self.configurationProvider.setEnvironment(self.__environment)
        self.__solver = CloudAcoProblemSolver()
        self.__solver.initialize(self.__environment, self.__colony, self.configurationProvider)
        startPheromoneMatrix = StartPheromoneMatrix()
        startPheromoneMatrix.setEnvironment(self.__environment)
        workflowUpdatePheromoneMatrix = WorkflowUpdatePheromoneMatrix()
        workflowUpdatePheromoneMatrix.setEnvironment(self.__environment)
        self.__solver.addCloudACODaemonActions(startPheromoneMatrix, workflowUpdatePheromoneMatrix)
        self.__solver.getAntColony().addAntPolicies(CloudAcoPseudoRandomNodeSelection())
        
        self.__mCloudAcoWorkflow = None
        
    def OptimiseWorkFlow(self, graph, resourceSet, bandwidth, deadline):
        self.__mCloudAcoWorkflow = CloudAcoWorkflow(graph, resourceSet , bandwidth, deadline)
        return self.__mCloudAcoWorkflow
    
    def setLacoSort(self, sortedTaskIds):
        self.__problemRepresentation.lacoSort(sortedTaskIds)
        return self.__mCloudAcoWorkflow
    
    def solve(self):
        self.__mCloudAcoWorkflow.solve().solveProblem()

    def printSolution(self):
        print("Cost: " + self.__mCloudAcoWorkflow.colony.getSolutionCost() + "\n" + self.__mCloudAcoWorkflow.colony.getSolution())
    
    def getAntColony(self, configurationProvider):
        tmp = CloudAcoAntColony(configurationProvider.getNumberOfAnts())
        return tmp
    

"""