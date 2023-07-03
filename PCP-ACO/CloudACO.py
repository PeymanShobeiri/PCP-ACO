from ACO.CloudAcoProblemNode import CloudAcoProblemNode
from prettytable import PrettyTable
from threading import Thread, Lock
from Constants import Constants
from ypstruct import structure
import numpy as np
import random
import copy
import sys

lock2 = Lock()


class CloudACO:

    def __init__(self):
        # ACO Parameters
        self.MaxIt = 500
        self.nAnt = 10
        self.H_RATIO = 5
        self.P_RATIO = 1
        self.EVAP_RATIO = 0.1
        self.Q0 = 0.8

        self.pheromone = None
        self.heuristic = []
        self.probability = []
        self.h_matrix = None
        self.__colony = []
        self.environment = None
        self.heuristicCache = {}
        # testing ...
        self.workflow = None
        self.deadline = 0

    def initPheromone(self, env):
        instance_NO = (env.getProblemGraph().getResourceSet().getSize()) * (
            env.getProblemGraph().getGraph().getMaxParallel()) + 5
        
        self.pheromone = np.full((instance_NO, instance_NO), 0.04)

    def initColony(self, antCount, graphSize):
        start = self.environment.getProblemGraph().getStart()
        self.__colony = [None] * antCount
        for k in range(antCount):
            ant = self.Ant(k, graphSize)
            ant.solution[0] = start
            self.__colony[k] = ant

    def getBandwidthDuration(self, node, parent):
        duration = float(parent.getDataSize()) / (Constants.BANDWIDTH * 1.0)
        return round(duration)

    def getNewStartTime(self, node):
        max_EFT = 0
        for parent in node.getParents():
            parentNode = self.environment._graph.nodes.get(parent.getId())
            if parentNode.getEFT() + self.getBandwidthDuration(node, parent) >= max_EFT:
                max_EFT = parentNode.getEFT() + self.getBandwidthDuration(node, parent)
        return max_EFT

    def getHeuristicValue(self, destination, task):
        curCost = destination.getCost(task)
        currentDuration = destination.getTaskDuration(task)
        currentST = max(destination.getInstanceReleaseTime(), self.getNewStartTime(task), 0)
        currentFT = currentST + currentDuration

        hc = self.HeuristicCondition(currentDuration, curCost, currentST, destination.getResource().getId(), task.getDeadline())

        if not str(task.getId()).lower() == "end" and not str(
                task.getId()).lower() == "start":
            if currentFT > task.getLFT():
                return 0.0

        if hc in self.heuristicCache:
            return self.heuristicCache[hc]

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

        for entry in self.environment._instances.instances.items():
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

        result = ((h1 * p1) + (h2 * p2)) / ratio

        if bad:
            result = result ** 2

        self.heuristicCache[hc] = result
        return result

    def calculateHeuristic(self, candidateNodes, positionInSolution, curtask):
        bestOptionIndex = -1
        bestOption = -1
        best = -1
        bestIndex = -1
        for i in range(len(candidateNodes)):
            # self.heuristic[i] = self.getHeuristicValue(candidateNodes[i], positionInSolution, curtask)
            if self.heuristic[i] >= bestOption:
                bestOption = self.heuristic[i]
                bestOptionIndex = i
            self.probability[i] = (self.heuristic[i] ** self.H_RATIO) * (
                self.pheromone[curtask.getMatrixId()][candidateNodes[i].getInstanceId()])
            if self.probability[i] >= best:
                best = self.probability[i]
                bestIndex = i

        return bestOptionIndex, bestIndex

    def rwsSelection(self, candidates, probabilities):
        value = random.random()
        total = 0.0
        node = None
        i = 0

        while i < len(candidates) and total < value:
            node = candidates[i]
            probability = probabilities[i].val
            if probability is None:
                raise RuntimeError("The probability for component " + node + " is not a number.")

            total += probability
            i += 1

        return node

    def getSolutionCost(self):
        tmp = self.environment.getProblemGraph().getProblemNodeList()
        usedTime = 0
        totalTime = 0
        result = 0
        for inst in tmp:
            result += inst.getTotalCost()
            if inst.getTotalCost() != 0:
                usedTime += inst.totalDuration
                totalTime += inst.totaltime
        # print(usedTime/(totalTime * 3600))
        t = usedTime / (totalTime * 3600)
        return result, t

    def releasePheromone(self, bestAnt):
        if bestAnt.solutionCost != 0:
            value = self.EVAP_RATIO * (1 / bestAnt.solutionCost) + 0.05
            i = 1
            while i < len(bestAnt.solution) and not bestAnt.solution[i + 1].getId().lower() == "end":
                self.pheromone[bestAnt.solution[i].getSelectedResource().getInstanceId()][
                    bestAnt.solution[i].getMatrixId()] = (self.pheromone[bestAnt.solution[
                    i].getSelectedResource().getInstanceId()][bestAnt.solution[i].getMatrixId()] * (
                                                                  1 - self.EVAP_RATIO)) + value
                i += 1

    def updatePheromone(self, ant):
        self.releasePheromone(ant)

    def localUpdate(self):
        self.pheromone = (1 - self.EVAP_RATIO) * self.pheromone + (self.EVAP_RATIO * 0.04) + 0.001  # + 0.02

    def move(self, currentAnt):
        # with lock:
        currentAnt.currentNode = self.workflow.getGraph().getNodes()["start"]
        currentAnt.solution[0] = self.workflow.getGraph().getNodes()["start"]
        currentAnt.currentPosition = 0
        while not currentAnt.isCompleted:
            curtask = currentAnt.currentNode.getNeighbourhood(self.environment)
            candidateNodes = self.environment.getProblemGraph().getProblemNodeList()
            bestOptionByHeuristic, bestOptionByProbability = self.calculateHeuristic(currentAnt, candidateNodes,
                                                                                     currentAnt.currentPosition,
                                                                                     curtask)

            if random.random() < self.Q0:
                dest = candidateNodes[bestOptionByProbability]
            else:
                dest = self.rwsSelection(candidateNodes, self.probability)

            dest.setCurrentTask(dest, self.environment, curtask)
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
        self.environment.getProblemGraph().getInstanceSet().resetPerAnt()
        self.environment.getProblemGraph().resetProblemNodeList()
        self.environment.getProblemGraph().resetNodes()

    def schedule(self, environment, deadline):
        self.environment = environment
        # Empty Ant
        empty_ant = structure()
        empty_ant.solution = []
        empty_ant.cost = 0.0

        # Best solution ever found
        bestAnt = empty_ant.deepcopy()
        bestAnt.cost = np.inf

        # Creating colony
        ant = empty_ant.repeat(self.nAnt)

        # Phromone Matrix
        self.pheromone = np.full((environment._graph.nodeNum + 3, environment._resources.size * environment._graph.maxParallel), 0.04)
        # self.heuristic = np.full(environment._graph.nodeNum, None)
        self.probability = np.full(environment._graph.nodeNum, None)

        # Creating heuristic information matrix
        self.h_matrix = np.full((environment._graph.nodeNum, environment._resources.size * environment._graph.maxParallel), None)
        row = 0
        for node in environment.sortedWorkflowNodes:
            if node.id == "start" or node.id == "end":
                continue
            for ins in environment.problemNodeList:
                tmp = structure()
                tmp.cost = ins.resource.costPerInterval
                # tmp.duration = round(node.instructionSize / ins.resource.MIPS)
                # tmp.startTime = ins.currentStartTime
                tmp.heuristic = self.getHeuristicValue(ins, node)
                tmp.probability = (tmp.heuristic ** self.H_RATIO) * ((self.pheromone[row][ins.instanceId]) ** self.P_RATIO)

                if self.probability[row] is None or self.probability[row].val < tmp.probability:
                    best_probability = structure()
                    best_probability.val = tmp.probability
                    best_probability.id = ins.instanceId
                    self.probability[row] = best_probability

                self.h_matrix[row, ins.instanceId] = tmp
            row += 1

        # ACO main loop
        for it in range(self.MaxIt):
            # Move Ants
            for j in range(self.nAnt):
                ant[j].solution.append(environment._graph.startNode)
                for k in range(1, environment._graph.nodeNum):
                    curTask = environment.sortedWorkflowNodes[k]
                    candidateNodes = environment.problemNodeList
                    # bestOptionByProbability = self.probability[k].id
                    #
                    # if random.random() < self.Q0:
                    #     dest = candidateNodes[(bestOptionByProbability // environment._graph.maxParallel) + (bestOptionByProbability % environment._graph.maxParallel)]
                    # else:
                    #     dest = self.rwsSelection(candidateNodes, self.probability)
                    #
                    # out = dest.setCurrentTask(dest, environment, curTask)
                    # if out.sw == 1:
                    #     for r in range(len(self.h_matrix)):
                    #         tmp2 = structure()
                    #         tmp2.cost = out.newinst.resource.costPerInterval
                    #         tmp2.heuristic = self.getHeuristicValue(out.newinst, environment.sortedWorkflowNodes[r])
                    #         tmp2.probability = (tmp2.heuristic ** self.H_RATIO) * ((self.pheromone[r][out.newinst.instanceId]) ** self.P_RATIO)
                    #
                    #         if self.probability[r] is None or self.probability[r].val < tmp2.probability:
                    #             best_probability = structure()
                    #             best_probability.val = tmp2.probability
                    #             best_probability.id = out.newinst.instanceId
                    #             self.probability[r] = best_probability
                    #         self.h_matrix[r][out.newinst.instanceId] = tmp2
                    ant[j].solution.append(curTask)

        # workflow = environment.getProblemGraph()
        # self.workflow = environment.getProblemGraph()
        # self.deadline = deadline
        # self.environment = environment
        # self.initPheromone(environment)
        # itr = 0
        # while itr < self.MaxIt:
        #     start = self.environment.getProblemGraph().getStart()
        #
        #     for x in range(self.nAnt):
        #         ant = self.Ant(x, workflow.getGraphSize())
        #         self.move(ant)
        #
        #     self.updatePheromone(self.__bestAnt)
        #
        #     itr += 1
        #
        # print("best ant utils is : " + str(self.__bestAnt.Utils))
        # # self.__bestAnt.saveSolution()
        # return self.__bestAnt.solutionCost

    class Ant:
        def __init__(self, id=None, size=0):

            self.isCompleted = False
            self.id = id
            self.solution = [None] * size
            self.Utils = 0
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

    class HeuristicCondition():
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
