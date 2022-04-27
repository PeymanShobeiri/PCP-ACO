from .Environment import Environment
from .exception import ConfigurationException
import logging
import datetime 

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)

class AntColony(Environment):
    def __init__(self,numberOfAnts):
        self.__numberOfAnts = numberOfAnts
        self.__hive = []
        self.__antPolicies = []
        self.__timeLimit = None
        self.__colonyIndex = None
        logger.info("Number of Ants in Colony: " + numberOfAnts)

    def createAnt(self, environment):
        raise ConfigurationException("You need to override the createAnt method and provide " +
                "a suitable Ant instance for your problem.")

    def buildColony(self, environment):
        for i in range(self.__numberOfAnts):
            self.__hive.append(self.createAnt(environment))

    def getBestPerformingAnt(self, environment):
        bestAnt = self.__hive[0]
        for ant in self.__hive:
            if ant.isSolutionReady(environment) and ant.ant.getSolutionCost(environment) < bestAnt.getSolutionCost(environment):
                bestAnt = ant
        
        return bestAnt
    
    def getHive(self):
        return self.__hive
    
    def clearAntSolutions(self):
        logger.log(logging.DEBUG,"CLEARING ANT SOLUTIONS")

        for ant in self.__hive:
            ant.clear()

    def shouldTerminateExecution(self, executionStartTime):
        if self.__timeLimit != None and executionStartTime != None:
            elapsedTime = executionStartTime - datetime.datetime.now()

            if elapsedTime > self.__timeLimit:
                logger.warning("TIMEOUT: Finishing solution generation after " + elapsedTime.seconds +" seconds.")

                return True
        
        return False
                

    def buildSolutions(self, environment, configurationProvider, executionStartTime):
        logger.log(logging.DEBUG, "BUILDING ANT SOLUTIONS")

        antCounter = 0

        if len(self.__hive) == 0:
            raise ConfigurationException(   "Your colony is empty: You have no ants to solve the problem. "
                            + "Have you called the buildColony() method?. Number of ants from configuration provider: " +
                            configurationProvider.getNumberOfAnts())
                        
        for ant in self.__hive:
            logger.info(f"Current ant: {antCounter}")

            while not ant.isSolutionReady(environment):
                ant.selectNextNode(environment, configurationProvider)
            
            ant.doAfterSolutionIsReady(environment, configurationProvider)
            logger.log(logging.DEBUG, "Solution is ready > Cost: {} , Solution: {}".format(ant.getSolutionCost(environment), ant.getSolutionAsString()))

            if self.shouldTerminateExecution(executionStartTime):
                return True
            antCounter += 1
        
        return False


    def addAntPolicies(self, antPolicies):
        self.__antPolicies.extend(antPolicies)
        hive = self.getHive()
        for ant in hive:
            for antPolicy in antPolicies:
                ant.ant.addPolicy(antPolicy)

    def setTimeLimit(self, timeLimit):
        self.__timeLimit = timeLimit
    
    def setColonyIndex(self , colonyIndex):
        self.__colonyIndex = colonyIndex

    def getColonyIndex(self):
        return self.__colonyIndex

    def getNumberOfAnts(self):
        return self.__numberOfAnts
    
    def setNumberOfAnts(self, numberOfAnts):
        self.__numberOfAnts = numberOfAnts
    
    def __str__(self):
        return "AntColony{" +\
                "numberOfAnts=" + self.__numberOfAnts +\
                ", antPolicies=" + self.__antPolicies +\
                ", colonyIndex=" + self.__colonyIndex +\
                '}'


