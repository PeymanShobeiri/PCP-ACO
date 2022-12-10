from ACO.pyisula.DaemonAction import DaemonAction
from .exception.ConfigurationException import ConfigurationException
from .Environment import Environment
from .PerformanceTracker import PerformanceTracker
import datetime
from .DaemonActionType import DaemonActionType
from .ConfigurationProvider import ConfigurationProvider
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)

class AcoProblemSolver(Environment):

    def __init__(self):
        self.__bestSolution = []
        self.__bestSolutionCost = 0.0
        self.__executionTime = 0.0
        self.__bestSolutionAsString = ""

        self.__environment = None
        self.__antColony = None

        self.__configurationProvider = ConfigurationProvider()
        self.__daemonActions = []
        self.__totalGeneratedSolutions = None

    def setConfigurationProvider(self, configurationProvider):
        self.__configurationProvider = configurationProvider

    def getConfigurationProvider(self):
        if self.__configurationProvider is None:
            raise ConfigurationException("No Configuration Provider was associated with this solver")
        
        return self.__configurationProvider

    def setEnvironment(self, environment):
        self.__environment = environment

    def configureAntColony(self, colony, environment, timeLimit):
        colony.buildColony(environment)
        colony.setTimeLimit(timeLimit)

    def setAntColony(self, antColony):
        self.__antColony = antColony

    def initialize1(self, environment, colony, config, timeLimit):
        self.setConfigurationProvider(config)
        self.setEnvironment(environment)

        if colony == None:
            raise ConfigurationException("The problem solver needs an instance of AntColony to be initialized")
        
        self.configureAntColony(colony, environment, timeLimit)
        self.setAntColony(colony)

    def initialize(self, environment, colony, config):
        self.initialize1(environment, colony, config, None)

    def configureDaemonAction(self, antColony, daemonAction, environment):
        daemonAction.setAntColony(antColony)
        daemonAction.setEnvironment(environment)
        daemonAction.setProblemSolver(self)

    def addDaemonAction(self, daemonAction):
        self.configureDaemonAction(self.__antColony , daemonAction, self.__environment)
        self.__daemonActions.append(daemonAction)


    def  addDaemonActions(self, daemonActions):
        for daemonAction in daemonActions:
            self.addDaemonAction(daemonAction)

    def applyDaemonActions(self, antColony, daemonActionType):
        for daemonAction in self.__daemonActions:
            if daemonAction.getAntColony() == antColony and daemonActionType == daemonAction.getAcoPhase():
                daemonAction.applyDaemonAction(self.getConfigurationProvider())

    def kickOffColony(self, antColony, environment, executionStartTime):
        self.applyDaemonActions(antColony, DaemonActionType.DaemonActionType().INITIAL_CONFIGURATION)

        logger.info(" Colony index: " + antColony.getColonyIndex() + " STARTING ITERATIONS")
        numberOfIterations = self.__configurationProvider.getNumberOfIterations()

        if numberOfIterations < 1:
            raise ConfigurationException("No iterations are programed for this solver. Check your Configuration Provider.")
        
        logger.info(" Colony index: " + antColony.getColonyIndex() + " Number of iterations: " + numberOfIterations)

        iteration = 0
        performanceTracker = performanceTracker()
        while iteration < numberOfIterations:
            iterationStart = datetime.datetime.now()
            antColony.clearAntSolutions()

            terminateExecution = antColony.buildSolutions(environment, self.__configurationProvider,executionStartTime)
            self.applyDaemonActions(antColony, DaemonActionType.DaemonActionType().AFTER_ITERATION_CONSTRUCTION)
            iterationEnd = datetime.datetime.now()
            iterationTime = (iterationEnd - iterationStart).seconds

            performanceTracker.updateIterationPerformance(antColony, iteration, iterationTime, environment)
            iteration += 1

            if terminateExecution:
                break
                
        return performanceTracker

    def updateGlobalMetrics(self, executionStartTime , performanceTracker):
        self.__bestSolution = performanceTracker.getBestSolution()
        self.__bestSolutionCost = performanceTracker.getBestSolutionCost()
        self.__bestSolutionAsString = performanceTracker.getBestSolutionAsString()
        self.__totalGeneratedSolutions = performanceTracker.getGeneratedSolutions()

        logger.info("Finishing computation at: " + datetime.datetime.now())
        executionEndTime = datetime.datetime.now()
        self.__executionTime = (executionEndTime - executionStartTime).seconds
        logger.info("Duration (in seconds): " + self.__executionTime)

        logger.info("EXECUTION FINISHED");
        logger.info("Solutions generated: " + self.__totalGeneratedSolutions)
        logger.info("Best solution cost: " + self.__bestSolutionCost)
        logger.info("Best solution:" + self.__bestSolutionAsString)


    def solveProblem(self):
        logger.info("Starting computation at:" + str(datetime.datetime.now()))
        executionStartTime = datetime.datetime.now()

        performanceTracker = self.kickOffColony(self.__antColony, self.__environment, executionStartTime)

        self.updateGlobalMetrics(executionStartTime, performanceTracker)

    def updateIterationPerformance(self, bestAnt, iteration, iterationTimeInSeconds, environment):
        logger.log(logging.DEBUG,"GETTING BEST SOLUTION FOUND")

        bestIterationCost = bestAnt.getSolutionCost(environment)
        logger.info("Iteration best cost: " + bestIterationCost)

        if self.__bestSolution == None or self.__bestSolutionCost > bestIterationCost:
            self.__bestSolution = bestAnt.getSolution()
            self.__bestSolutionCost = bestIterationCost
            self.__bestSolutionAsString = bestAnt.getSolutionAsString()

            logger.info("Best solution so far > Cost: " + self.__bestSolutionCost+ ", Solution: " + self.__bestSolutionAsString)
        
        logger.info("Current iteration: " + iteration + " Iteration best: " + bestIterationCost + " Best solution cost: "+\
                + self.__bestSolutionCost + " Iteration Duration (s): " + iterationTimeInSeconds)
        
    
    def getEnvironment(self):
        return self.__environment
    
    def getAntColony(self):
        return self.__antColony
    
    def getBestSolution(self):
        return self.__bestSolution
    
    def getBestSolutionCost(self):
        return self.__bestSolutionCost
    
    def getBestSolutionAsString(self):
        return self.__bestSolutionAsString

    def getDaemonActions(self):
        return self.__daemonActions

    def __str__(self) :
        return "AcoProblemSolver{" +\
                "bestSolution=" + self.__bestSolution +\
                ", bestSolutionCost=" + self.__bestSolutionCost +\
                ", executionTime=" + self.__executionTime +\
                ", environment=" + self.__environment +\
                ", antColony=" + self.__antColony +\
                ", configurationProvider=" + self.__configurationProvider +\
                ", daemonActions=" + self.__daemonActions +\
                ", totalGeneratedSolutions=" + self.__totalGeneratedSolutions +\
                '}'