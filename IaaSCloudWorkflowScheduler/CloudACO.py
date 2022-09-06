import random
import sys
from threading import Thread, Lock
import matplotlib.pyplot as plt
from Constants import Constants
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from ACO.CloudAcoResourceInstance import CloudAcoResourceInstance
from ACO.CloudAcoProblemNode import CloudAcoProblemNode
import copy
from prettytable import PrettyTable

import threading
import concurrent.futures

lock = Lock()
lock2 = Lock()


class CloudACO:

    def __init__(self, sol_size):
        self.__H_RATIO = 2
        self.__P_RATIO = 1
        self.__EVAP_RATIO = 0.05
        self.__Q0 = 0.88
        self.__iterCount = 100
        self.__antCount = 30
        self.__pheromone = None
        self.__heuristic = []
        self.__probability = []
        self.__colony = []
        self.__bestAnt = self.Ant(size=sol_size)
        self.__globalant = None
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
        self.__pheromone = np.full((instance_NO, instance_NO), 1)

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

        hc = self.HeuristicCondition(currentDuration, curCost, currentST, destination.getResource().getId())

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
                    (task.getLFT() - task.getDeadline()) + 1 * 1.0)))
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

        h3 = (slowest - currentDuration + 1) / (slowest - fastest + 1)
        # h3 = 1 / (curCost+1)
        h2 = ((maxCost - curCost + 1) / (maxCost - minCost + 1))
        p1 = 5
        p2 = 5
        p3 = 5
        ratio = p1 + p2 + p3
        if positionInSolution < self.__environment.getProblemGraph().getGraphSize() / 3:
            p1 = 11
            p2 = 2
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

    def calculateHeuristic(self, candidateNodes, positionInSolution, curtask):
        bestOptionIndex = -1
        bestOption = -1
        for i in range(len(candidateNodes)):
            self.__heuristic[i] = self.getHeuristicValue(candidateNodes[i], positionInSolution, curtask)
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
                    self.__pheromone[current.currentNode.getSelectedResource().getInstanceId()][
                        candidateNodes[i].getInstanceId()] ** self.__P_RATIO)
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
            value = 1 / bestAnt.solutionCost + 0.5
            i = 0
            while i < len(bestAnt.solution) - 1 and not bestAnt.solution[i + 1].getId().lower() == "end":
                self.__pheromone[bestAnt.solution[i].getSelectedInstance()][bestAnt.solution[i+1].getSelectedInstance()] += value
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
        currentAnt.currentNode = self.workflow.getGraph().getNodes()["start"]
        currentAnt.solution[0] = self.workflow.getGraph().getNodes()["start"]
        currentAnt.currentPosition = 0
        while not currentAnt.isCompleted:
            curtask = currentAnt.currentNode.getNeighbourhood(self.__environment)
            candidateNodes = self.__environment.getProblemGraph().getProblemNodeList()
            bestOptionByHeuristic = self.calculateHeuristic(candidateNodes, currentAnt.currentPosition, curtask)
            bestOptionByProbability = self.calculateProbability(currentAnt, candidateNodes)

            if random.random() < self.__Q0:
                dest = candidateNodes[bestOptionByProbability]
            else:
                dest = self.rwsSelection(candidateNodes, self.__probability)

            # currentAnt.currentNode.setVisited(self.__environment)
            # dest.setVisited(self.__environment)
            dest.setCurrentTask(dest, self.__environment, curtask)
            currentAnt.setDest(curtask)

        end = currentAnt.solution[len(currentAnt.solution) - 2]
        currentAnt.makeSpan = end.getAFT()

        currentAnt.solutionCost = self.getSolutionCost()  # check that if it's calculation is ok

        # print("end of ant")
        # print("cA : " + str(currentAnt.solutionCost) + " MK : " + str(currentAnt.makeSpan))
        if self.__bestAnt.id is None and currentAnt.makeSpan <= self.deadline:
            self.__bestAnt = copy.deepcopy(currentAnt)
            # self.__bestAnt.saveSolution()
            print("best ant: " + str(self.__bestAnt.solutionCost))

        elif currentAnt.solutionCost < self.__bestAnt.solutionCost and currentAnt.makeSpan <= self.deadline:
            self.__bestAnt = copy.deepcopy(currentAnt)
            # self.__bestAnt.saveSolution()
            # self.__bestAnt.saveSolution2()
            print("best ant: " + str(self.__bestAnt.solutionCost))

        self.__environment.getProblemGraph().getInstanceSet().resetPerAnt()
        self.__environment.getProblemGraph().resetProblemNodeList()
        self.__environment.getProblemGraph().resetNodes()

    def schedule(self, environment, deadline):
        workflow = environment.getProblemGraph()
        self.workflow = environment.getProblemGraph()
        self.deadline = deadline
        self.__environment = environment
        self.initPheromone(environment)
        itr = 0
        while itr < self.__iterCount:
            self.initColony(self.__antCount, workflow.getGraphSize())
            currentAnt = None
            # self.__heuristicCache = {}
            dest = None
            antNum = 0

            for x in range(self.__antCount):
                self.move(x)
            # threads = []
            # for x in range(self.__antCount):
            #     y = (x,)
            #     t = Thread(target=self.move, args=y)
            #     t.start()
            #     threads.append(t)
            #
            # for thr in threads:
            #     thr.join()

            self.updatePheromone()

            # if self.__globalant is None:
            #     self.__globalant = copy.deepcopy(self.__bestAnt)
            #     print("first xxx is  :   " + str(self.__globalant.solutionCost))
            # elif self.__globalant.solutionCost > self.__bestAnt.solutionCost:
            #     self.__globalant = copy.deepcopy(self.__bestAnt)
            #     print("gloooooooooooballlllllllllllll is  :   " + str(self.__globalant.solutionCost))
            #
            # self.__bestAnt.solutionCost = 0
            # self.__bestAnt.makeSpan = 0
            # self.__bestAnt.id = None

            itr += 1

        print("best ant best: " + str(self.__bestAnt.solutionCost))
        self.__bestAnt.saveSolution()
        # self.__globalant.saveSolution2()
        return self.__bestAnt.solutionCost

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

            # temp = []
            # temp.append(str(node.getId()))
            # temp.append(str(node.getSelectedResource().getId()))
            # temp.append(str(node.getSelectedResource().getInstanceId()))
            # temp.append(str(node.getSelectedResource().getTotalCost()))
            # temp.append(str(node.getSelectedResource().getResource().getCost()))
            # temp.append(str(node.getAST()))
            # temp.append(str(node.getRunTime()))
            # temp.append(str(node.getAFT()))
            # temp.append(str(node.getDeadline()))
            # temp.append(str(node.getLFT()))
            # temp.append(str(node.getSelectedResource().getInstanceStartTime()))
            # # temp.append(str(node.h)[0:min(4, len(str(node.h)))])
            #
            # rowsList.append(temp)

            # val2 = [i for i in range(len(rowsList))]
            # fig, ax = plt.subplots()
            # ax.set_axis_off()
            # table = ax.table(
            #     cellText=rowsList,
            #     rowLabels=val2,
            #     colLabels=headersList,
            #     rowColours=["skyblue"] * len(rowsList),
            #     colColours=["skyblue"] * 12,
            #     cellLoc='center',
            #     loc='upper right')
            #
            # ax.set_title('id {}'.format(self.id),
            #              fontweight="bold")
            # # table.set_fontsize(24)
            # table.scale(1, 1.5)
            # plt.show()

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
