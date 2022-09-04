import random
import sys
from threading import Thread, Lock
import matplotlib.pyplot as plt
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from ACO.CloudAcoResourceInstance import CloudAcoResourceInstance
from ACO.CloudAcoProblemNode import CloudAcoProblemNode
import copy

import threading
import concurrent.futures

lock = Lock()
lock2 = Lock()
globalAnt = None

class CloudACO:

    def __init__(self, sol_size):
        self.__H_RATIO = 0.6
        self.__P_RATIO = 0.4
        self.__EVAP_RATIO = 0.1
        self.__Q0 = 0.9
        self.__iterCount = 200
        self.__antCount = 20
        self.__pheromone = None
        self.__heuristic = []
        self.__probability = []
        self.__colony = []
        self.globalant = None
        self.__bestAnt = self.Ant(size=sol_size)
        self.__environment = None
        self.__heuristicCache = dict()
        # testing ...
        self.workflow = None
        self.deadline = 0

    def initPheromone(self, size):
        self.__heuristic = np.zeros(size)
        self.__probability = np.zeros(size)
        self.__pheromone = np.full((size, size), 1)

    def initColony(self, antCount, graphSize):
        start = self.__environment.getProblemGraph().getStart()
        self.__colony = [None] * antCount
        for k in range(antCount):
            ant = self.Ant(k, graphSize)
            # ant.solution.append(start)
            ant.solution[0] = start
            self.__colony[k] = ant

    def getNewStartTime(self, node):
        max_AFT = 0
        for parent in node.getParents():
            parentNode = self.__environment.getProblemGraph().getGraph().getNodes().get(parent.getId())
            if parentNode.getAFT() >= max_AFT:
                max_AFT = parentNode.getAFT()  # + self.getBandwidthDuration(node)
        return max_AFT

    def getHeuristicValue(self, destination, positionInSolution):
        curCost = destination.getResource().getCost(destination.getNode())
        currentDuration = destination.getResource().getTaskDuration(destination.getNode())
        currentST = max(destination.getResource().getInstanceReleaseTime(), self.getNewStartTime(destination.getNode()),
                        0)
        currentFT = currentST + currentDuration

        hc = self.HeuristicCondition(currentDuration, curCost, currentST, destination.getResource().getId())

        if not str(destination.getNode().getId()).lower() == "end" and not str(
                destination.getNode().getId()).lower() == "start":
            if currentFT > destination.getNode().getLFT():
                return 0.0

        if hc in self.__heuristicCache:
            return self.__heuristicCache[hc]

        h1 = 0.0
        h2 = 0.0

        bad = False

        if currentFT <= destination.getNode().getDeadline():
            h1 = 1
        else:
            h1 = max(0, (((destination.getNode().getLFT() - currentFT) + 1) / (
                    (destination.getNode().getLFT() - destination.getNode().getDeadline()) + 1 * 1.0)))
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
                temp = instance.getCost(destination.getNode())
                tempDuration = instance.getTaskDuration(destination.getNode())
                if temp > maxCost:
                    maxCost = temp
                elif temp < minCost:
                    minCost = temp

                if tempDuration > slowest:
                    slowest = tempDuration
                elif tempDuration < fastest:
                    fastest = tempDuration

        h3 = (slowest - currentDuration + 1) / (slowest - fastest + 1)
        h2 = ((maxCost - curCost + 1) / (maxCost - minCost + 1))
        p1 = 5
        p2 = 5
        p3 = 5
        ratio = p1 + p2 + p3
        if positionInSolution < self.__environment.getProblemGraph().getGraphSize() / 3:
            p1 = 2
            p2 = 11
            p3 = 2
        elif positionInSolution > (2 * (self.__environment.getProblemGraph().getGraphSize() / 3)):
            p1 = 2
            p2 = 11
            p3 = 2

        result = ((h1 * p1) + (h2 * p2) + (h3 * p3)) / ratio

        if bad:
            result = result ** 2
            # result = pow(result, 2)

        self.__heuristicCache[hc] = result
        return result

    def calculateHeuristic(self, candidateNodes, positionInSolution):
        bestOptionIndex = -1
        bestOption = -1
        for i in range(len(candidateNodes)):
            self.__heuristic[i] = self.getHeuristicValue(candidateNodes[i], positionInSolution)
            candidateNodes[i].h = self.__heuristic[i]
            if self.__heuristic[i] >= bestOption:
                bestOption = self.__heuristic[i]
                bestOptionIndex = i

        # print("sum is : " + str(sum(self.__heuristic)))
        # bestOptionIndex = np.argmax(self.__heuristic)
        return bestOptionIndex

    def calculateProbability(self, current, candidateNodes):
        best = -1
        bestIndex = -1
        i = 0
        while i < len(candidateNodes):
            self.__probability[i] = (self.__heuristic[i] ** self.__H_RATIO) * (
                    self.__pheromone[current.currentNode.getId()][candidateNodes[i].getId()] ** self.__P_RATIO)
            if self.__probability[i] >= best:
                best = self.__probability[i]
                bestIndex = i
            i += 1

        self.__probability = self.__probability / sum(self.__probability)
        # print(self.__probability)

        return bestIndex

    def rwsSelection(self, candidates, probabilities):
        value = random.random()
        total = 0.0
        node = None
        i = 0

        if candidates[0].getNode().getId() == 'end':
            return candidates[0]

        y = np.cumsum(probabilities)
        ss = np.argmax(y >= value)
        candidates[ss].setByRW = True
        return candidates[ss]

    def getSolutionCost(self):
        tmp = self.__environment.getProblemGraph().getInstanceSet().getInstances()
        tmp = list(tmp.values())
        result = 0
        for inst in tmp:
            for k in inst:
                result += k.getTotalCost()
        return result

    def releasePheromone(self, bestAnt):
        value = 1 / bestAnt.solutionCost + 0.5
        i = 0
        while i < len(bestAnt.solution) - 1 and not bestAnt.solution[i + 1].getNode().getId().lower() == "end":
            self.__pheromone[bestAnt.solution[i].getId()][bestAnt.solution[i + 1].getId()] += value
            i += 1

    def updatePheromone(self):
        self.__pheromone = self.__pheromone * (1 - self.__EVAP_RATIO)

        if self.__bestAnt is not None:
            self.releasePheromone(self.__bestAnt)

        self.__pheromone[self.__pheromone > 1] = 1
        self.__pheromone[self.__pheromone < 0.2] = 0.2

    def move(self, antNum):
        # with lock:
        currentAnt = self.__colony[antNum]
        currentAnt.currentNode = self.workflow.getStart()
        currentAnt.currentPosition = 0
        currentAnt.currentNode.setVisited(self.__environment)
        with lock:
            while not currentAnt.isCompleted:
                candidateNodes = currentAnt.currentNode.getNeighbourhood(self.__environment)
                bestOptionByHeuristic = self.calculateHeuristic(candidateNodes, currentAnt.currentPosition)
                bestOptionByProbability = self.calculateProbability(currentAnt, candidateNodes)

                if random.random() < self.__Q0:
                    dest = candidateNodes[bestOptionByProbability]
                else:
                    dest = self.rwsSelection(candidateNodes, self.__probability)

                # currentAnt.currentNode.setVisited(self.__environment)
                dest.setVisited(self.__environment)
                dest.getResource().setCurrentTask(dest, self.__environment)
                currentAnt.setDest(dest)

            end = currentAnt.solution[len(currentAnt.solution) - 2]
            currentAnt.makeSpan = end.getNode().getAFT()

            currentAnt.solutionCost = self.getSolutionCost()
            # print("CA : " + str(currentAnt.solutionCost) + " MS : " + str(currentAnt.makeSpan))
            # currentAnt.saveSolution()
            # currentAnt.saveSolution2()
            if self.__bestAnt.id is None and currentAnt.makeSpan <= self.deadline:
                self.__bestAnt = copy.deepcopy(currentAnt)
                # self.__bestAnt.saveSolution()
                print("best ant: " + str(self.__bestAnt.solutionCost))
            elif currentAnt.solutionCost < self.__bestAnt.solutionCost and currentAnt.makeSpan <= self.deadline:
                self.__bestAnt = copy.deepcopy(currentAnt)
                # self.__bestAnt.saveSolution()
                # self.__bestAnt.saveSolution2()
                print("best ant: " + str(self.__bestAnt.solutionCost))
            # self.updatePheromone()

            self.__environment.getProblemGraph().getInstanceSet().resetPerAnt()
            self.__environment.getProblemGraph().resetNodes()

    def schedule(self, environment, deadline):
        global globalAnt
        workflow = environment.getProblemGraph()
        self.workflow = environment.getProblemGraph()
        self.deadline = deadline
        self.__environment = environment
        self.initPheromone(len(environment.getProblemGraph().getProblemNodeList()))
        itr = 0
        while itr < self.__iterCount:
            self.initColony(self.__antCount, workflow.getGraphSize())
            currentAnt = None
            self.__heuristicCache = {}
            dest = None
            antNum = 0

            threads = []
            for x in range(self.__antCount):
                y = (x,)
                t = Thread(target=self.move, args=y)
                t.start()
                threads.append(t)

            for thr in threads:
                thr.join()

            # with ThreadPoolExecutor(max_workers=self.__antCount) as executer:
            #     res = executer.map(self.move, self.__colony)
            #
            # print(list(res))

            self.updatePheromone()
            if globalAnt is None:
                globalAnt = copy.deepcopy(self.__bestAnt)
            elif globalAnt.solutionCost > self.__bestAnt.solutionCost:
                globalAnt = copy.deepcopy(self.__bestAnt)
            # self.__bestAnt.saveSolution.
            self.__bestAnt = self.Ant(size=environment.getProblemGraph().getGraphSize())
            itr += 1

        print("best ant best: " + str(globalAnt.solutionCost))
        globalant.saveSolution()
        globalAnt.saveSolution2()
        return globalAnt.solutionCost

    class Ant:
        def __init__(self, id=None, size=0):

            self.isCompleted = False
            self.id = id
            self.solution = []
            for _ in range(size):
                self.solution.append(CloudAcoProblemNode())
            self.solutionString = ""
            self.solutionCost = 0.0
            self.makeSpan = 0.0
            self.currentNode = None
            self.currentPosition = 0

        def setDest(self, node):
            self.currentNode = node
            self.currentPosition += 1

            self.solution[self.currentPosition] = node
            if (node.getNode().getId()).lower() == "end" or self.currentPosition == len(self.solution):
                self.isCompleted = True
            # return self.currentPosition

        def __str__(self):
            return self.solutionString

        def saveSolution(self):
            headersList = ["N", "R", "I", "I-cost", "R-cost", "AST", "runtime", "AFT", "SD", "LFT", "I-start", "H"]

            rowsList = []
            for node in self.solution:
                if node is None:
                    continue

                runtime = node.getResource().getTaskDuration(node.getNode())
                temp = []
                temp.append(str(node.getNode().getId()))
                temp.append(str(node.getResource().getId()))
                temp.append(str(node.getResource().getInstanceId()))
                temp.append(str(node.getResource().getTotalCost()))
                temp.append(str(node.getResource().getResource().getCost()))
                temp.append(str(node.getNode().getAST()))
                temp.append(str(runtime)[0:min(4, len(str(runtime)))])
                temp.append(str(node.getNode().getAFT()))
                temp.append(str(node.getNode().getDeadline()))
                temp.append(str(node.getNode().getLFT()))
                temp.append(str(node.getResource().getInstanceStartTime()))
                temp.append(str(node.h)[0:min(4, len(str(node.h)))])

                rowsList.append(temp)

            val2 = [i for i in range(len(rowsList))]
            fig, ax = plt.subplots()
            ax.set_axis_off()
            table = ax.table(
                cellText=rowsList,
                rowLabels=val2,
                colLabels=headersList,
                rowColours=["skyblue"] * len(rowsList),
                colColours=["skyblue"] * 12,
                cellLoc='center',
                loc='upper right')

            ax.set_title('id {}'.format(self.id),
                         fontweight="bold")
            # table.set_fontsize(24)
            table.scale(1, 1.5)
            plt.show()

        def saveSolution2(self):
            headersList = ["N", "R", "I", "I-cost", "R-cost", "AST", "runtime", "AFT", "SD", "LFT", "I-start", "H"]

            rowsList = []
            for node in self.solution:
                if node is None:
                    continue

                runtime = node.getResource().getTaskDuration(node.getNode())
                temp = []
                temp.append(str(node.getNode().getId()))
                temp.append(str(node.getResource().getId()))
                temp.append(str(node.getResource().getInstanceId()))
                temp.append(str(node.getResource().getTotalCost()))
                temp.append(str(node.getResource().getResource().getCost()))
                temp.append(str(node.getNode().getAST()))
                temp.append(str(runtime)[0:min(4, len(str(runtime)))])
                temp.append(str(node.getNode().getAFT()))
                temp.append(str(node.getNode().getDeadline()))
                temp.append(str(node.getNode().getLFT()))
                temp.append(str(node.getResource().getInstanceStartTime()))
                temp.append(str(node.h)[0:min(4, len(str(node.h)))])

                rowsList.append(temp)

            val2 = [i for i in range(len(rowsList))]
            fig, ax = plt.subplots()
            ax.set_axis_off()
            table = ax.table(
                cellText=rowsList,
                rowLabels=val2,
                colLabels=headersList,
                rowColours=["skyblue"] * len(rowsList),
                colColours=["skyblue"] * 12,
                cellLoc='center',
                loc='lower right')

            # ax.set_title('cost {}'.format(self._solutionCost),
            #              fontweight="bold")
            # table.set_fontsize(24)
            table.scale(1, 1.5)
            plt.show()

        # @property
        # def solution(self):
        #     return self.solution

    class HeuristicCondition(object):
        def __init__(self, curDuration, curCost, curStartTime, instanceId):
            self.__curDuration = curDuration
            self.__curCost = curCost
            self.__curStartTime = curStartTime
            self.__instanceId = instanceId

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
            return (self.__curCost, self.__curDuration, self.__curStartTime, self.__instanceId)

        def __hash__(self):
            return hash(self.__key())
