from abc import ABC

from Environment import Environment
import logging
from exception import SolutionConstructionException

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)


class PerformanceTracker(Environment, ABC):

    def __init__(self, problemRepresentation):
        super().__init__(problemRepresentation)
        self.__bestSolution = None
        self.__bestSolutionCost = 0.0
        self.__bestSolutionAsString = ""
        self.__generatedSolutions = 0

    def isStateValid(self, ant, environment):
        if self.__bestSolution is None and self.__bestSolutionAsString == "" and self.__bestSolutionCost == 0.0:
            return True

        expectedSolutionCost = ant.getSolutionCost(environment, self.__bestSolution)
        expectedSolutionAsString = ant.getSolutionAsString(self.__bestSolution)

        if abs(expectedSolutionCost - self.__bestSolutionCost) <= 0.001 and expectedSolutionAsString == self.__bestSolutionAsString:
            return True

        return False

    def updateIterationPerformance(self, antColony, iteration, iterationTimeInSeconds, environment):
        logger.log(logging.DEBUG, "GETTING BEST SOLUTION FOUND")

        tmp = [ant for ant in antColony.getHive() if ant.isSolutionReady(environment) == True]
        iterationSolutions = len(tmp)  # .count in java

        self.__generatedSolutions += iterationSolutions

        bestAnt = antColony.getBestPerformingAnt(environment)

        if not self.isStateValid(bestAnt, environment):
            raise SolutionConstructionException

        bestIterationCost = bestAnt.getSolutionCost(environment)
        logger.info("Iteration best cost: " + bestIterationCost)

        if self.__bestSolution is None or self.__bestSolutionCost > bestIterationCost:
            self.__bestSolution = bestAnt.getSolution()
            if self.__bestSolution is None:
                raise Exception("finded NONE ")

            self.__bestSolutionCost = bestIterationCost
            self.__bestSolutionAsString = bestAnt.getSolutionAsString()

            logger.info("Best solution so far > Cost: " + self.__bestSolutionCost + \
                        ", Solution as string: " + self.__bestSolutionAsString + " Stored solution: " + self.__bestSolution)

        logger.info(
            " Colony index: " + antColony.getColonyIndex() + " Current iteration: " + iteration + " Iteration solutions: " + iterationSolutions +
            " Iteration best: " + bestIterationCost + " Iteration Duration (s): " + iterationTimeInSeconds +
            " Global solution cost: " + self.__bestSolutionCost)
        logger.info(
            " Global solution cost: " + self.__bestSolutionCost + " Stored solution: " + self.__bestSolution + " Solution as String: " + self.__bestSolutionAsString)

    def getBestSolution(self):
        return self.__bestSolution

    def getBestSolutionCost(self):
        return self.__bestSolutionCost

    def getBestSolutionAsString(self):
        return self.__bestSolutionAsString

    def getGeneratedSolutions(self):
        return self.__generatedSolutions

    def setGeneratedSolutions(self, generatedSolutions):
        self.__generatedSolutions = generatedSolutions
