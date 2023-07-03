from ACO.CloudAcoProblemNode import CloudAcoProblemNode
from concurrent.futures import ThreadPoolExecutor
from prettytable import PrettyTable
from Constants import Constants
from ypstruct import structure
import numpy as np
import random
import copy
import time


class CloudACO:

    def __init__(self):
        # ACO Parameters
        self.MaxIt = 400
        self.nAnt = 10
        self.H_RATIO = 5
        self.P_RATIO = 1
        self.EVAP_RATIO = 0.1
        self.Q0 = 0.8

        self.pheromone = None
        self.heuristic = None
        self.probability = []
        self.h_matrix = None
        self.finished = None
        self.__colony = []
        self.environment = None
        self.heuristicCache = {}

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

    def calculateHeuristic(self, candidateNodes, curtask):

        best = -1
        bestIndex = -1
        for i in range(len(candidateNodes)):
            sw = 0
            currentDuration = round(curtask.instructionSize / candidateNodes[i].resource.MIPS)

            curCost = candidateNodes[i].getCost(currentDuration)

            currentST = max(candidateNodes[i].currentStartTime, self.finished[curtask.id])
            currentFT = currentST + currentDuration

            hc = self.HeuristicCondition(currentDuration, curCost, currentST, candidateNodes[i].instanceId, curtask.subDeadline)

            if not str(curtask.id).lower() == "end" and not str(curtask.id).lower() == "start":
                if currentFT > curtask.LFT:
                    result = 0.0
                    sw = 1

            if hc in self.heuristicCache:
                result = self.heuristicCache[hc]
                sw = 2

            if sw == 0:
                h1 = 0.0
                h2 = 0.0

                bad = False

                if currentFT <= curtask.subDeadline:
                    h1 = 1
                else:
                    h1 = max(0, (((curtask.LFT - currentFT) + 1) / (
                            (curtask.LFT - curtask.subDeadline) + 1)))
                    bad = True

                maxCost = -1
                minCost = np.inf
                fastest = np.inf
                slowest = 0
                temp = 0.0
                tempDuration = 0.0

                for instance in self.environment._instances.instances:
                    tempDuration = round(curtask.instructionSize / instance.resource.MIPS)
                    temp = instance.getCost(tempDuration)

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

            self.probability[i] = (result ** self.H_RATIO) * (self.pheromone[curtask.getMatrixId()][candidateNodes[i].getInstanceId()] ** self.P_RATIO)
            if self.probability[i] >= best:
                best = self.probability[i]
                bestIndex = i

        return bestIndex

    def rwsSelection(self, candidates, probabilities):
        value = random.random()
        probabilities = probabilities / probabilities.sum()
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
        tmp = self.environment.problemNodeList
        usedTime = 0
        totalTime = 0
        result = 0
        for inst in tmp:
            result += inst.totalCost
            if inst.totalCost != 0:
                usedTime += inst.totalDuration
                totalTime += inst.totaltime
        # print(usedTime/(totalTime * 3600))
        t = usedTime / (totalTime * 3600)
        return result, t

    def updatePheromone(self, bestAnt):
        if bestAnt.cost != 0:
            value = self.EVAP_RATIO * (1 / bestAnt.cost) + 0.05
            i = 1
            while i < len(bestAnt.solution) and not bestAnt.solution[i + 1].getId().lower() == "end":

                self.pheromone[bestAnt.solution[i].getMatrixId()][bestAnt.solution[i].getSelectedResource().getInstanceId()] = (self.pheromone[bestAnt.solution[i].getMatrixId()][bestAnt.solution[i].getSelectedResource().getInstanceId()] * (
                                                                  1 - self.EVAP_RATIO)) + value
                i += 1

    def localUpdate(self):
        self.pheromone = (1 - self.EVAP_RATIO) * self.pheromone + (self.EVAP_RATIO * 0.04) + 0.001  # + 0.02

    def resetProblemNodeList(self):
        problemNodeList = []
        mId = 0

        for instance in self.environment._instances.instances:
            problemNodeList.append(instance)

        for curNode in self.environment.sortedWorkflowNodes:
            if curNode.getId() == "start":
                # self.__start = curNode
                curNode.setMatrixId(0)
                curNode.setSelectedResource(problemNodeList[len(problemNodeList)-1])

            elif curNode.getId() == "end":
                # self.__end = curNode
                curNode.setMatrixId(mId)
                curNode.setSelectedResource(problemNodeList[len(problemNodeList)-1])
            else:
                curNode.setMatrixId(mId)
                mId += 1

        return problemNodeList

    def resetNodes(self):
        for node in self.environment._graph.nodes.items():
            curnode = node[1]
            if curnode.id == "start" or curnode.id == "end":
                curnode.selectedResource = self.environment.problemNodeList[-1]
            else:
                curnode.selectedResource = -1
            curnode.selectedInstance = -1
            curnode.AST = None
            if curnode.id == "start":
                curnode.AFT = 0
            else:
                curnode.AFT = None

    def schedule(self, environment, deadline):
        self.environment = environment
        # Empty Ant
        empty_ant = structure()
        empty_ant.solution = []
        empty_ant.cost = 0.0
        empty_ant.makeSpan = 0.0
        empty_ant.Utils = 0.0

        # Best solution ever found
        bestAnt = empty_ant.deepcopy()
        bestAnt.cost = np.inf
        bestAnt.makeSpan = np.inf
        bestAnt.Utils = 0.0

        # Creating colony
        ant = empty_ant.repeat(self.nAnt)

        # Phromone Matrix
        self.pheromone = np.full((environment._graph.nodeNum + 3, environment._resources.size * environment._graph.maxParallel), 0.04)
        self.probability = np.full(environment._resources.size * environment._graph.maxParallel, 0.0)

        # Create the finished dictionary
        self.finished = {"start": 0, "end": deadline}

        # Creating heuristic information matrix
        # self.h_matrix = np.full((environment._graph.nodeNum, environment._resources.size * environment._graph.maxParallel), None)
        # row = 0
        # for node in environment.sortedWorkflowNodes:
        #     if node.id == "start" or node.id == "end":
        #         continue
        #     for ins in environment.problemNodeList:
        #         tmp = structure()
        #         tmp.cost = ins.resource.costPerInterval
        #         tmp.duration = round(node.instructionSize / ins.resource.MIPS)
        #         tmp.startTime = ins.currentStartTime
        #         tmp.heuristic = 0.0
        #
        #         self.h_matrix[row, ins.instanceId] = tmp
        #     row += 1

        # ACO main loop
        for it in range(self.MaxIt):
            # Move Ants
            for j in range(self.nAnt):
                ant[j].solution.append(environment._graph.startNode)
                for k in range(1, environment._graph.nodeNum):
                    curTask = environment.sortedWorkflowNodes[k]
                    candidateNodes = environment.problemNodeList

                    # A matrix for finish times for each node
                    mx = 0
                    for parent in curTask.parents:
                        P_AFT = self.environment._graph.nodes.get(parent.getId()).AFT
                        if P_AFT > mx:
                            mx = P_AFT
                    self.finished[curTask.id] = mx

                    bestOptionByProbability = self.calculateHeuristic(candidateNodes, curTask)

                    if random.random() < self.Q0:
                        dest = candidateNodes[bestOptionByProbability]
                    else:
                        dest = self.rwsSelection(candidateNodes, self.probability)

                    dest.setCurrentTask(dest, environment, curTask, self.h_matrix, self.finished)

                    ant[j].solution.append(curTask)

                ant[j].makeSpan = ant[j].solution[-2].AFT
                ant[j].cost, ant[j].Utils = self.getSolutionCost()

                if ant[j].cost < bestAnt.cost and ant[j].makeSpan <= deadline:
                    bestAnt = ant[j].deepcopy()
                    print("best ant: " + str(bestAnt.cost))


                self.localUpdate()
                self.environment._instances.resetPerAnt()
                self.environment.problemNodeList = self.resetProblemNodeList()
                self.resetNodes()
                return 

            self.updatePheromone(bestAnt)

    class HeuristicCondition:
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
