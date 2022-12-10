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
        self.__iterCount = 500
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
        # size = env.getProblemGraph().getGraph().getNodeNum() + 5
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
            # ant.solution.append(start)
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

        if curCost == 0:
            print("ssss")
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

        # maxCost = list(self.__environment.getProblemGraph().getInstanceSet().getInstances().items())[0][1][0].getCost(task)
        # minCost = list(self.__environment.getProblemGraph().getInstanceSet().getInstances().items())[9][1][0].getCost(task)

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

        h3 = (slowest - currentDuration + 1) / (slowest - fastest + 1)
        # h1 = (max(abs(slowest-task.getDeadline()), abs(task.getDeadline() - fastest)) - abs(currentDuration - task.getDeadline()) + 1) / (max(abs(slowest-task.getDeadline()), abs(task.getDeadline() - fastest)) + 1)

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
            # if positionInSolution == 1 and self.__heuristic[i] == 0.0 and bestOption == 0.0:
            #     print("help")
            if self.__heuristic[i] >= bestOption:
                bestOption = self.__heuristic[i]
                bestOptionIndex = i
            self.__probability[i] = (self.__heuristic[i] ** self.__H_RATIO) * (
                self.__pheromone[candidateNodes[i].getInstanceId()][curtask.getMatrixId()])
            if self.__probability[i] >= best:
                best = self.__probability[i]
                bestIndex = i

        # print("sum is : " + str(sum(self.__heuristic)))
        # bestOptionIndex = np.argmax(self.__heuristic)

        return bestOptionIndex, bestIndex

    # def calculateProbability(self, current, candidateNodes):
    #     best = -1
    #     bestIndex = -1
    #     i = 0
    #     while i < len(candidateNodes):
    #         self.__probability[i] = (self.__heuristic[i] ** self.__H_RATIO) * (
    #             self.__pheromone[current.currentNode.getSelectedResource().getInstanceId()][
    #                 candidateNodes[i].getInstanceId()])
    #         if self.__probability[i] >= best:
    #             best = self.__probability[i]
    #             bestIndex = i
    #         i += 1
    #
    #     # self.__probability = self.__probability / sum(self.__probability)
    #     # print(self.__probability)
    #
    #     return bestIndex

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
        result = 0
        for inst in tmp:
            result += inst.getTotalCost()
        return result

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
        # self.__pheromone = self.__pheromone * (1 - self.__EVAP_RATIO)

        # if self.__bestAnt is not None:
        self.releasePheromone(ant)

        # self.__pheromone[self.__pheromone > 1] = 1
        # self.__pheromone[self.__pheromone < 0.2] = 0.2

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
            # print("h: " + str(bestOptionByHeuristic) + " p : " + str(bestOptionByProbability), end=" ,")
            # bestOptionByProbability = self.calculateProbability(currentAnt, candidateNodes)

            if random.random() < self.__Q0:
                dest = candidateNodes[bestOptionByProbability]
            else:
                dest = self.rwsSelection(candidateNodes, self.__probability)

            dest.setCurrentTask(dest, self.__environment, curtask)
            currentAnt.setDest(curtask)

        end = currentAnt.solution[len(currentAnt.solution) - 2]
        currentAnt.makeSpan = end.getAFT()

        currentAnt.solutionCost = self.getSolutionCost()  # check that if it's calculation is ok

        # print("end of ant")
        # print("cA : " + str(currentAnt.solutionCost) + " MK : " + str(currentAnt.makeSpan) + "  "+ str(antNum))
        with lock2:
            if self.__bestAnt.id is None and currentAnt.makeSpan <= self.deadline:
                self.__bestAnt = copy.deepcopy(currentAnt)
                # self.__bestAnt.saveSolution()
                print("best ant: " + str(self.__bestAnt.solutionCost))

            elif currentAnt.solutionCost < self.__bestAnt.solutionCost and currentAnt.makeSpan <= self.deadline:
                self.__bestAnt = copy.deepcopy(currentAnt)
                # self.__bestAnt.saveSolution()
                # self.__bestAnt.saveSolution2()
                print("best ant: " + str(self.__bestAnt.solutionCost))

            # self.updatePheromone(currentAnt)
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

            # with ThreadPoolExecutor() as executor:
            #     executor.map(self.move, self.__colony)
            # print(__name__)
            # process = []
            # # pp = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            # for x in range(self.__antCount):
            #     y = self.Ant(x, workflow.getGraphSize())
            #     p = Process(target=self.move, args=(y,))
            #     p.start()
            #     process.append(p)
            #
            # for ptr in process:
            #     ptr.join()

            # with ProcessPoolExecutor() as executor:
            #     executor.map(self.move, [0, 1])

            # threads = []
            # for x in range(self.__antCount):
            #     y = self.Ant(x, workflow.getGraphSize())
            #     t = Thread(target=self.move, args=(y,))
            #     t.start()
            #     threads.append(t)
            #
            # for thr in threads:
            #     thr.join()

            self.updatePheromone(self.__bestAnt)

            itr += 1

        print("best ant best: " + str(self.__bestAnt.solutionCost))
        self.__bestAnt.saveSolution()
        return self.__bestAnt.solutionCost

    class Ant:
        def __init__(self, id=None, size=0):

            self.isCompleted = False
            self.id = id
            self.solution = []
            for _ in range(size):
                self.solution.append(None)
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
            # headersList = ["N", "R", "I", "I-cost", "R-cost", "AST", "runtime", "AFT", "SD", "LFT", "I-start"]
            # for h in headersList:
            #     print(h, end=' ')
            # print()
            # print("---------------------------------------------------------------------------------------")
            # rowsList = []
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
