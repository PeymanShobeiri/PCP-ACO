from .pyisula.exception.ConfigurationException import ConfigurationException
from .pyisula.AcoProblemSolver import AcoProblemSolver
from .pyisula.DaemonActionType import DaemonActionType


class CloudAcoProblemSolver(AcoProblemSolver):
    
    def __init__(self):
        self.__bestSolution = None
        self.__environment = None
        self.__antColony = None
        self.__configurationProvider = None
        self.__daemonActions = []

    def setCloudAcoAntColony(self, cloudAcoAntColony):
        self.__antColony = cloudAcoAntColony

    # Prepares the solver for problem resolution.
    def initialize(self, environment, colony, config):
        colony.buildColony(environment)
        self.setConfigurationProvider(config)
        self.setEnvironment(environment)
        self.setCloudAcoAntColony(colony)

    def applyDaemonActions(self , daemonActionType):
        for daemonAction in self.__daemonActions:
            if daemonActionType == daemonAction.getAcoPhase():
                daemonAction.applyDaemonAction(self.getConfigurationProvider())

    def addCloudACODaemonActions(self, daemonActions):
        for daemonAction in daemonActions:
            self.addDaemonAction(daemonAction)
    
    def addDaemonAction(self, daemonAction):
        daemonAction.setAntColony(self.__antColony)
        daemonAction.setEnvironment(self.__environment)
        daemonAction.setProblemSolver(self)
        self.__daemonActions.append(daemonAction)

    def solveProblem(self):
        self.applyDaemonActions(DaemonActionType().INITIAL_CONFIGURATION)
        numberOfIterations = self.__configurationProvider.getNumberOfIterations()
        if numberOfIterations < 1:
            raise ConfigurationException("No iterations are programed for this solver. Check your Configuration Provider.")
        else:
            for iteration in range(numberOfIterations):
                self.__antColony.clearAntSolutions()
                self.__antColony.buildSolutions(self.__environment, self.__configurationProvider)
                self.applyDaemonActions(DaemonActionType().AFTER_ITERATION_CONSTRUCTION)
                print("Current iteration: " + iteration + " Best solution cost: " + self.__antColony.getSolutionCost())
            
            print("Best solution cost: " + self.__antColony.getSolutionCost())
            print("Best solution:\n" + self.__antColony.getSolution())
        
    def getEnvironment(self):
        return self.__environment
    
    def setEnvironment(self, environment):
        self.__environment = environment
    
    def getAntColony(self):
        return self.__antColony
    
    def setAntColony(self, antColony):
        self.setAntColony(antColony)
    
    def getConfigurationProvider(self):
        return self.__configurationProvider
    
    def setConfigurationProvider(self, configurationProvider):
        self.__configurationProvider = configurationProvider
    
    def getBestSolution(self):
        return self.__bestSolution
    
    def getBestSolutionCost(self):
        return self.__antColony.getSolutionCost()

    def setBestSolutionCost(self, bestSolutionCost):
        pass
    
    def getBestSolutionAsString(self):
        return self.__antColony.getSolution()
        