import random
import sys
from threading import Thread, Lock
import matplotlib.pyplot as plt
from Constants import Constants
import numpy as np
from ACO.CloudAcoResourceInstance import CloudAcoResourceInstance
from ACO.CloudAcoProblemNode import CloudAcoProblemNode
import copy
from prettytable import PrettyTable
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import threading
import concurrent.futures
from multiprocessing import Process

lock = Lock()
lock2 = Lock()
globalAnt = None


class CloudACO:

    def __init__(self, sol_size):
        self.__H_RATIO = 5
        self.__P_RATIO = 1
        self.__EVAP_RATIO = 0.1
        self.__Q0 = 0.8
        self.__iterCount = 400
        self.__antCount = 10
        self.__pheromone = None
        self.__heuristic = []
        self.__probability = []
        self.__colony = []
        self.__bestAnt = self.Ant(size=sol_size)
        # self.__globalant = None
        self.__environment = None
        self.__heuristicCache = {}
        # testing ...
        self.workflow = None
        self.deadline = 0

    def initPheromone(self, env):
        instance_NO = (env.getProblemGraph().getResourceSet().getSize()) * (
            env.getProblemGraph().getGraph().getMaxParallel()) + 5
        self.__heuristic = np.zeros(instance_NO)
        self.__probability = np.zeros(instance_NO)
        self.__pheromone = np.full((instance_NO, instance_NO), 0.04)

    def initColony(self, antCount, graphSize):
        start = self.__environment.getProblemGraph().getStart()
        self.__colony = [None] * antCount
        for k in range(antCount):
            ant = self.Ant(k, graphSize)
            ant.solution[0] = start
            self.__colony[k] = ant

    def getBandwidthDuration(self, node, parent):
        duration = float(parent.getDataSize()) / (Constants.BANDWIDTH * 1.0)
        return round(duration)

    def getNewStartTime(self, node):
        max_AFT = 0
        for parent in node.getParents():
            parentNode = self.__environment.getProblemGraph().getGraph().getNodes().get(parent.getId())
            if parentNode.getAFT() + self.getBandwidthDuration(node, parent) >= max_AFT:
                max_AFT = parentNode.getAFT() + self.getBandwidthDuration(node, parent)
        return max_AFT

    def getHeuristicValue(self, destination, positionInSolution, task):
        curCost = destination.getCost(task)
        currentDuration = destination.getTaskDuration(task)
        currentST = max(destination.getInstanceReleaseTime(), self.getNewStartTime(task),
                        0)
        currentFT = currentST + currentDuration

        hc = self.HeuristicCondition(currentDuration, curCost, currentST, destination.getResource().getId(),
                                     task.getDeadline())

        if not str(task.getId()).lower() == "end" and not str(
                task.getId()).lower() == "start":
            if currentFT > task.getLFT():
                return 0.0

        if hc in self.__heuristicCache:
            return self.__heuristicCache[hc]

        h1 = 0.0
        h2 = 0.0

        bad = False

        if currentFT <= task.getDeadline():
            h1 = 1
        else:
            h1 = max(0, (((task.getLFT() - currentFT) + 1) / (
                    (task.getLFT() - task.getDeadline()) + 1)))
            bad = True

        maxCost = -1
        minCost = sys.maxsize
        fastest = sys.maxsize
        slowest = 0
        temp = 0.0
        tempDuration = 0.0

        for entry in self.__environment.getProblemGraph().getInstanceSet().getInstances().items():
            test3 = entry[1]  # test3 is the instance on the each resource
            for instance in test3:
                temp = instance.getCost(task)
                tempDuration = instance.getTaskDuration(task)
                if temp > maxCost:
                    maxCost = temp
                if temp < minCost:
                    minCost = temp

                if tempDuration > slowest:
                    slowest = tempDuration
                if tempDuration < fastest:
                    fastest = tempDuration

        h2 = ((maxCost - curCost + 1) / (maxCost - minCost + 1))

        p1 = 1
        p2 = 1
        ratio = p1 + p2
        if positionInSolution <= self.__environment.getProblemGraph().getGraphSize() / 3:
            p1 = 1
            p2 = 1
        elif positionInSolution > (2 * (self.__environment.getProblemGraph().getGraphSize() / 3)):
            p1 = 1
            p2 = 1

        result = ((h1 * p1) + (h2 * p2)) / ratio

        if bad:
            result = result ** 2

        self.__heuristicCache[hc] = result
        return result

    def calculateHeuristic(self, current, candidateNodes, positionInSolution, curtask):
        bestOptionIndex = -1
        bestOption = -1
        best = -1
        bestIndex = -1
        for i in range(len(candidateNodes)):
            self.__heuristic[i] = self.getHeuristicValue(candidateNodes[i], positionInSolution, curtask)
            if self.__heuristic[i] >= bestOption:
                bestOption = self.__heuristic[i]
                bestOptionIndex = i
            self.__probability[i] = (self.__heuristic[i] ** self.__H_RATIO) * (
                self.__pheromone[candidateNodes[i].getInstanceId()][curtask.getMatrixId()])
            if self.__probability[i] >= best:
                best = self.__probability[i]
                bestIndex = i

        return bestOptionIndex, bestIndex

    def rwsSelection(self, candidates, probabilities):
        value = random.random()
        total = 0.0
        node = None
        i = 0

        while i < len(candidates) and total < value:
            node = candidates[i]
            probability = probabilities[i]
            if probability is None:
                raise RuntimeError("The probability for component " + node + " is not a number.")

            total += probability
            i += 1

        return node

    def getSolutionCost(self):
        tmp = self.__environment.getProblemGraph().getProblemNodeList()
        usedTime = 0
        totalTime = 0
        result = 0
        for inst in tmp:
            result += inst.getTotalCost()
            if inst.getTotalCost() != 0:
                usedTime += inst.totalDuration
                totalTime += inst.totaltime
        # print(usedTime/(totalTime * 3600))
        t = usedTime/(totalTime * 3600)
        return result, t

    def releasePheromone(self, bestAnt):
        if bestAnt.solutionCost != 0:
            value = self.__EVAP_RATIO * (1 / bestAnt.solutionCost) + 0.05
            i = 1
            while i < len(bestAnt.solution) and not bestAnt.solution[i + 1].getId().lower() == "end":
                self.__pheromone[bestAnt.solution[i].getSelectedResource().getInstanceId()][
                    bestAnt.solution[i].getMatrixId()] = (self.__pheromone[bestAnt.solution[
                    i].getSelectedResource().getInstanceId()][bestAnt.solution[i].getMatrixId()] * (
                                                                  1 - self.__EVAP_RATIO)) + value
                i += 1

    def updatePheromone(self, ant):
        self.releasePheromone(ant)

    def localUpdate(self):
        self.__pheromone = (1 - self.__EVAP_RATIO) * self.__pheromone + (self.__EVAP_RATIO * 0.04) + 0.001  # + 0.02

    def move(self, currentAnt):
        # with lock:
        currentAnt.currentNode = self.workflow.getGraph().getNodes()["start"]
        currentAnt.solution[0] = self.workflow.getGraph().getNodes()["start"]
        currentAnt.currentPosition = 0
        while not currentAnt.isCompleted:
            curtask = currentAnt.currentNode.getNeighbourhood(self.__environment)
            candidateNodes = self.__environment.getProblemGraph().getProblemNodeList()
            bestOptionByHeuristic, bestOptionByProbability = self.calculateHeuristic(currentAnt, candidateNodes, currentAnt.currentPosition, curtask)

            if random.random() < self.__Q0:
                dest = candidateNodes[bestOptionByProbability]
            else:
                dest = self.rwsSelection(candidateNodes, self.__probability)

            dest.setCurrentTask(dest, self.__environment, curtask)
            currentAnt.setDest(curtask)

        end = currentAnt.solution[len(currentAnt.solution) - 2]
        currentAnt.makeSpan = end.getAFT()

        currentAnt.solutionCost, currentAnt.Utils = self.getSolutionCost()

        # with lock2:
        if self.__bestAnt.id is None and currentAnt.makeSpan <= self.deadline:
            self.__bestAnt = copy.deepcopy(currentAnt)
            print("best ant: " + str(self.__bestAnt.solutionCost))

        elif currentAnt.solutionCost < self.__bestAnt.solutionCost and currentAnt.makeSpan <= self.deadline:
            self.__bestAnt = copy.deepcopy(currentAnt)
            print("best ant: " + str(self.__bestAnt.solutionCost))

        self.localUpdate()
        self.__environment.getProblemGraph().getInstanceSet().resetPerAnt()
        self.__environment.getProblemGraph().resetProblemNodeList()
        self.__environment.getProblemGraph().resetNodes()

    def schedule(self, environment, deadline):
        global globalAnt
        globalAnt = None
        workflow = environment.getProblemGraph()
        self.workflow = environment.getProblemGraph()
        self.deadline = deadline
        self.__environment = environment
        self.initPheromone(environment)
        itr = 0
        while itr < self.__iterCount:
            start = self.__environment.getProblemGraph().getStart()

            for x in range(self.__antCount):
                ant = self.Ant(x, workflow.getGraphSize())
                self.move(ant)

            self.updatePheromone(self.__bestAnt)

            itr += 1

        print("best ant utils is : " + str(self.__bestAnt.Utils))
        # self.__bestAnt.saveSolution()
        return self.__bestAnt.solutionCost

    class Ant:
        def __init__(self, id=None, size=0):

            self.isCompleted = False
            self.id = id
            self.solution = [None]*size
            self.Utils = 0
            # for _ in range(size):
            #     self.solution.append(None)
            self.solutionString = ""
            self.solutionCost = 0.0
            self.makeSpan = 0.0
            self.currentNode = None
            self.currentPosition = 0

        def setDest(self, node):
            self.currentNode = node
            self.currentPosition += 1
            # print(self.currentPosition, end=" ")
            self.solution[self.currentPosition] = node
            if (node.getId()).lower() == "end" or self.currentPosition == len(self.solution) - 1:
                self.isCompleted = True
            # return self.currentPosition

        def __str__(self):
            return self.solutionString

        def saveSolution(self):
            myTable = PrettyTable(["N", "R", "I", "I-cost", "R-cost", "AST", "runtime", "AFT", "SD", "LFT", "I-start"])
            for node in self.solution:
                if node is None:
                    continue

                myTable.add_row([str(node.getId()), str(node.getSelectedResource().getId()),
                                 str(node.getSelectedResource().getInstanceId()),
                                 str(node.getSelectedResource().getTotalCost()),
                                 str(node.getSelectedResource().getResource().getCost()), str(node.getAST()),
                                 str(node.getRunTime()), str(node.getAFT()), str(node.getDeadline()),
                                 str(node.getLFT()), str(node.getSelectedResource().getInstanceStartTime())])
            print(myTable)
            print("cost is : " + str(self.solutionCost))

    class HeuristicCondition(object):
        def __init__(self, curDuration, curCost, curStartTime, instanceId, sd):
            self.__curDuration = curDuration
            self.__curCost = curCost
            self.__curStartTime = curStartTime
            self.__instanceId = instanceId
            self.__sd = sd

        def getCurDuration(self):
            return self.__curDuration

        def setCurDuration(self, curDuration):
            self.__curDuration = curDuration

        def getCurCost(self):
            return self.__curCost

        def setCurCost(self, curCost):
            self.__curCost = curCost

        def __eq__(self, other):
            if other.__curDuration == self.__curDuration and other.__curCost == self.__curCost and other.__curStartTime == self.__curStartTime and other.__instanceId == self.__instanceId:
                return True
            else:
                return False

        def __ne__(self, other):
            if other.__curDuration != self.__curDuration and other.__curCost != self.__curCost and other.__curStartTime != self.__curStartTime and other.__instanceId != self.__instanceId:
                return True
            else:
                return False

        def __key(self):
            return (self.__curCost, self.__curDuration, self.__curStartTime, self.__instanceId, self.__sd)

        def __hash__(self):
            return hash(self.__key())
