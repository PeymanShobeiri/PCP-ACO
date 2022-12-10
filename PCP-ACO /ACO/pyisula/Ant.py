from Environment import Environment
from abc import ABC, abstractmethod
from AntPolicyType import AntPolicyType
from exception import SolutionConstructionException, ConfigurationException


class Ant(ABC, Environment):
    def __init__(self):
        super().__init__()
        self.__DONT_CHECK_NUMBERS = -1
        self.__ONE_POLICY = 1
        self.__currentIndex = 0
        self.__policies = []
        self.__solution = []
        self.__visitedComponents = {}

    def getSolution(self):
        return self.__solution

    def getSolutionAsString(self, solution):
        if solution is not None:
            return ' '.join(solution)

    def getSolutionAsString(self):
        return self.getSolutionAsString(self.__solution)

    def visitNode(self, visitedNode, environment):
        if self.getSolution() is not None:
            self.getSolution().append(visitedNode)
            self.__visitedComponents[visitedNode] = True
            self.__currentIndex += 1
        else:
            print("Couldn't add component " + str(visitedNode) + " at index " + str(
                self.__currentIndex) + ". \nPartial solution is " + self.getSolutionAsString())
            raise SolutionConstructionException

    def setCurrentIndex(self, currentIndex):
        self.__currentIndex = currentIndex

    def clear(self):
        self.setCurrentIndex(0)

        if self.getSolution() is None:
            print("Couldn't clear solution since current solution is null. Verify" +
                  " each ant instance have the solution array properly initialized.")
            raise SolutionConstructionException
        self.getSolution().clear()
        self.__visitedComponents.clear()

    def addPolicy(self, antPolicy):
        self.__policies.append(antPolicy)

    def getAntPolicies(self, policyType, expectedNumber):
        selectedPolicies = []
        for policy in self.__policies:
            if policyType == policy.getPolicyType():
                selectedPolicies.append(policy)

        if 0 < expectedNumber != len(selectedPolicies):
            print("The number of" + policyType + " policies was " + str(len(
                selectedPolicies)) + ". We were expecting " + str(expectedNumber))
            raise ConfigurationException

        return selectedPolicies

    def selectNextNode(self, environment, configurationProvider):
        selectNodePolicity = self.getAntPolicies(AntPolicyType().NODE_SELECTION, self.__ONE_POLICY)[0]

        selectNodePolicity.setAnt(self)
        policyResult = selectNodePolicity.applyPolicy(environment, configurationProvider)
        if not policyResult:
            raise ConfigurationException

        afterNodeSelection = self.getAntPolicies(AntPolicyType().AFTER_NODE_SELECTION, self.__DONT_CHECK_NUMBERS)
        for antPolicy in afterNodeSelection:
            antPolicy.setAnt(self)
            antPolicy.applyPolicy(environment, configurationProvider)

    def doAfterSolutionIsReady(self, environment, configurationProvider):
        antPolicies = self.getAntPolicies(AntPolicyType().AFTER_SOLUTION_IS_READY, self.__DONT_CHECK_NUMBERS)

        for antPolicy in antPolicies:
            antPolicy.setAnt(self)
            antPolicy.applyPolicy(environment, configurationProvider)

    def isNodeVisited(self, component):
        visited = False
        inVisitedMap = self.__visitedComponents.get(component)

        if inVisitedMap != None and inVisitedMap:
            visited = inVisitedMap

        return visited

    # Calculates the cost associated to the solution build, which is needed to determine the performance of the Ant.
    @abstractmethod
    def getSolutionCost(self, environment, solution):
        pass

    def getSolutionCost(self, environment):
        return self.getSolutionCost(environment, self.__solution)

    def isNodeValid(self, node):
        return True

    def setCurrentIndex(self, currentIndex):
        self.__currentIndex = currentIndex

    def getCurrentIndex(self):
        return self.__currentIndex

    @abstractmethod
    def isSolutionReady(self, environment):
        pass

    @abstractmethod
    def getHeuristicValue(self, solutionComponent, environment):
        pass

    @abstractmethod
    def getNeighbourhood(self, environment):
        pass

    @abstractmethod
    def getPheromoneTrailValue(self, solutionComponent, positionInSolution, environment):
        pass

    @abstractmethod
    def setPheromoneTrailValue(self, solutionComponent, positionInSolution, environment, value):
        pass

    def getSolution(self):
        return self.__solution

    def setSolution(self, solution):
        self.__solution = solution

    def getVisited(self):
        return self.__visitedComponents

    def setVisited(self, visited):
        self.__visitedComponents = visited
