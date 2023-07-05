from ACO.CloudAcoProblemNode import CloudAcoProblemNode
from concurrent.futures import ThreadPoolExecutor
from prettytable import PrettyTable
from Constants import Constants
from ypstruct import structure
from threading import Lock
from math import ceil
import numpy as np
import pickle
import random
import copy
import time

lock = Lock()


class CloudACO:

    def __init__(self):
        # ACO Parameters
        self.MaxIt = 300
        self.nAnt = 10
        self.H_RATIO = 5
        self.P_RATIO = 1
        self.EVAP_RATIO = 0.1
        self.Q0 = 0.8
        self.PERIOD_DURATION = 3600

        self.pheromone = None
        self.heuristic = None
        self.probability = []
        self.h_matrix = None
        self.finished = None
        self.environment = None
        self.heuristicCache = {}

    def getBandwidthDuration(self, node, parent):
        duration = float(parent.getDataSize()) / (Constants.BANDWIDTH * 1.0)
        return round(duration)

    def calculateHeuristic(self, candidateNodes, curtask, finished):

        best = -1
        bestIndex = -1
        for i in range(len(candidateNodes)):
            sw = 0
            currentDuration = round(curtask.instructionSize / candidateNodes[i]["resource"].MIPS)

            curCost = 0

            countOfHoursToProvision = int(ceil(currentDuration / float(self.PERIOD_DURATION)))

            if countOfHoursToProvision == 0:
                countOfHoursToProvision = 1

            if candidateNodes[i]["currentTask"] is None:
                curCost = candidateNodes[i]["resource"].costPerInterval * countOfHoursToProvision
            else:
                if currentDuration <= candidateNodes[i]["instanceFinishTime"] - candidateNodes[i]["totalDuration"]:
                    curCost = 0
                else:
                    lack = currentDuration - candidateNodes[i]["instanceFinishTime"] - candidateNodes[i][
                        "totalDuration"]
                    countOfHoursToProvision = int(ceil(lack / float(self.PERIOD_DURATION)))
                    curCost = countOfHoursToProvision * candidateNodes[i]["resource"].costPerInterval

            # curCost = candidateNodes[i].getCost(currentDuration)

            currentST = max(candidateNodes[i]["currentStartTime"], finished[curtask.id])
            currentFT = currentST + currentDuration

            hc = self.HeuristicCondition(currentDuration, curCost, currentST, candidateNodes[i]["instanceId"],
                                         curtask.subDeadline)

            if not str(curtask.id) == "end" and not str(curtask.id) == "start":
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
                    tempDuration = round(curtask.instructionSize / instance["resource"].MIPS)

                    countOfHoursToProvision = int(ceil(tempDuration / float(self.PERIOD_DURATION)))

                    if countOfHoursToProvision == 0:
                        countOfHoursToProvision = 1

                    if instance["currentTask"] is None:
                        temp = instance["resource"].costPerInterval * countOfHoursToProvision
                    else:
                        if tempDuration <= instance["instanceFinishTime"] - instance["totalDuration"]:
                            temp = 0
                        else:
                            lack = tempDuration - instance["instanceFinishTime"] - instance["totalDuration"]
                            countOfHoursToProvision = int(ceil(lack / float(self.PERIOD_DURATION)))
                            temp = countOfHoursToProvision * instance["resource"].costPerInterval

                    # temp = instance.getCost(tempDuration)

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

            self.probability.append((result ** self.H_RATIO) * (
                        self.pheromone[curtask.getMatrixId()][candidateNodes[i]["instanceId"]] ** self.P_RATIO))
            if self.probability[i] >= best:
                best = self.probability[i]
                bestIndex = i

        return bestIndex

    def rwsSelection(self, candidates, probabilities):
        value = random.random()
        probabilities = probabilities / sum(probabilities)
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

    def getSolutionCost(self, tmp):
        usedTime = 0
        totalTime = 0
        result = 0
        for inst in tmp:
            result += inst["totalCost"]
            if inst["totalCost"] != 0:
                usedTime += inst["totalDuration"]
                totalTime += inst["totaltime"]
        t = usedTime / (totalTime * 3600)
        return result, t

    def updatePheromone(self, bestAnt):
        if bestAnt.cost != 0:
            value = self.EVAP_RATIO * (1 / bestAnt.cost) + 0.05
            for sol in bestAnt.solution:
                self.pheromone[int(sol["id"].split("ID")[1])][sol["selectedInstance"]] = ((self.pheromone[
                    int(sol["id"].split("ID")[1])][sol["selectedInstance"]]) * (1 - self.EVAP_RATIO)) + value

    def localUpdate(self):
        self.pheromone = (1 - self.EVAP_RATIO) * self.pheromone + (self.EVAP_RATIO * 0.04) + 0.001  # + 0.02

    def resetProblemNodeList(self):
        problemNodeList = []
        mId = 0

        for instance in self.environment._instances.instances:
            problemNodeList.append(instance)

        return problemNodeList

    def schedule(self, environment, deadline):
        self.environment = environment
        # Empty Ant
        empty_ant = structure()
        empty_ant.solution = []
        empty_ant.cost = 0.0
        empty_ant.makeSpan = 0.0
        empty_ant.Utils = 0.0
        empty_ant.problemNodeList = copy.deepcopy(self.environment.problemNodeList)
        empty_ant.finished = {"start": 0, "end": deadline}

        # Best solution ever found
        bestAnt = empty_ant.deepcopy()
        bestAnt.solution = []
        bestAnt.cost = np.inf
        bestAnt.makeSpan = np.inf
        bestAnt.Utils = 0.0

        # Creating colony
        ant = empty_ant.repeat(self.nAnt)

        # Phromone Matrix
        self.pheromone = np.full(
            (environment._graph.nodeNum + 3, environment._resources.size * environment._graph.maxParallel), 0.04)
        # self.probability = np.full(environment._resources.size * environment._graph.maxParallel, 0.0)

        # ACO main loop
        for it in range(self.MaxIt):
            # Move Ants
            for j in range(self.nAnt):
                AFT_Dic = {'start': 0}
                for k in range(1, environment._graph.nodeNum - 1):
                    curTask = environment.sortedWorkflowNodes[k]
                    candidateNodes = ant[j].problemNodeList

                    # A matrix for finish times for each node
                    mx = 0
                    for parent in curTask.parents:
                        if AFT_Dic[parent.id] > mx:
                            mx = AFT_Dic[parent.id]
                    ant[j].finished[curTask.id] = mx

                    bestOptionByProbability = self.calculateHeuristic(candidateNodes, curTask, ant[j].finished)

                    if random.random() < self.Q0:
                        dest = candidateNodes[bestOptionByProbability]
                    else:
                        dest = self.rwsSelection(candidateNodes, self.probability)

                    newTaskDuration = round(curTask.instructionSize / dest["resource"].MIPS)
                    countOfHoursToProvision = max(int(ceil(
                        (newTaskDuration - max(dest["instanceFinishTime"] - curTask.EST, 0)) / (
                                    self.PERIOD_DURATION * 1.0))), 0)
                    addedTimeToProvision = (countOfHoursToProvision * self.PERIOD_DURATION)

                    if dest["currentTask"] is None:
                        dest["instanceStartTime"] = ant[j].finished[curTask.id]
                        dest["taskStart"] = ant[j].finished[curTask.id]
                        dest["instanceFinishTime"] = addedTimeToProvision
                        dest["currentStartTime"] = round(ant[j].finished[curTask.id] + newTaskDuration)
                        dest["currentTaskDuration"] = newTaskDuration
                        dest["totalDuration"] += newTaskDuration
                        dest["totaltime"] = countOfHoursToProvision
                        dest["currentTask"] = curTask
                        dest["totalCost"] += countOfHoursToProvision * dest["resource"].costPerInterval

                        if dest["instanceId"] + 1 != environment._graph.maxParallel and not dest["instanceId"] + 1 >= environment._graph.maxParallel * environment._resources.size:
                            newinst = {"PERIOD_DURATION": 3600, "instanceId": dest["instanceId"] + 1,
                                       "resource": dest["resource"], "currentTask": None,
                                       "currentTaskDuration": 0, "totalDuration": 0, "totaltime": 0,
                                       "processedTasks": [],
                                       "processedTasksIds": set(), "currentStartTime": 0, "instanceFinishTime": 0.0,
                                       "totalCost": 0,
                                       "instanceStartTime": None, "taskStart": 0}
                            ant[j].problemNodeList.append(newinst)

                    else:
                        remain = dest["instanceFinishTime"] - dest["totalDuration"]
                        countOfHoursToProvision = max(
                            int(round((newTaskDuration - remain) / float(self.PERIOD_DURATION))), 0)
                        addedTimeToProvision = (countOfHoursToProvision * self.PERIOD_DURATION)
                        dest["instanceFinishTime"] += addedTimeToProvision
                        dest["taskStart"] = max(ant[j].finished[curTask.id], dest["currentStartTime"])
                        dest["currentStartTime"] = round(dest["taskStart"] + newTaskDuration)
                        dest["currentTaskDuration"] = newTaskDuration
                        dest["totalDuration"] += newTaskDuration
                        dest["totaltime"] += countOfHoursToProvision
                        dest["currentTask"] = curTask
                        dest["totalCost"] += countOfHoursToProvision * dest["resource"].costPerInterval

                    antNode = {"id": curTask.id, "AST": int(round(dest["taskStart"])),
                               "AFT": int(round(dest["taskStart"] + newTaskDuration)), "runTime": newTaskDuration,
                               "selectedInstance": dest["instanceId"]}

                    # dest["processedTasks"].append(node)
                    dest["processedTasksIds"].add(curTask.id)

                    ant[j].solution.append(antNode)
                    AFT_Dic[curTask.id] = antNode["AFT"]
                    self.probability = []

                ant[j].makeSpan = ant[j].solution[-1]["AFT"]
                ant[j].cost, ant[j].Utils = self.getSolutionCost(ant[j].problemNodeList)

                if ant[j].cost < bestAnt.cost and ant[j].makeSpan <= deadline:
                    bestAnt.solution = ant[j].solution
                    bestAnt.cost = ant[j].cost
                    bestAnt.Utils = ant[j].Utils
                    bestAnt.makeSpan = ant[j].makeSpan
                    print("best ant: " + str(bestAnt.cost))

                ant[j].solution = []
                self.localUpdate()
                # self.environment._instances.resetPerAnt()
                ant[j].problemNodeList = self.resetProblemNodeList()
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
