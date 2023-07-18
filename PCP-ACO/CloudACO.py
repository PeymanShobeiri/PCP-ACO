from concurrent.futures import ThreadPoolExecutor
from Constants import Constants
from ypstruct import structure
from threading import Lock, Thread
from math import ceil
import numpy as np
import random
import copy

lock = Lock()


class CloudACO:


    def __init__(self):
        # ACO Parameters
        self.MaxIt = 200
        self.nAnt = 5
        self.H_RATIO = 2
        self.P_RATIO = 1
        self.EVAP_RATIO = 0.1
        self.Q0 = 0.8
        self.PERIOD_DURATION = 3600

        self.pheromone = None
        self.environment = None
        self.heuristicCache = {}


    def getBandwidthDuration(self, node, parent):
        duration = (parent.getDataSize()) / (Constants.BANDWIDTH * 1.0)
        return round(duration)


    def calculateHeuristic(self, candidateNodes, curtask, finished, probability):

        best = -1
        bestIndex = -1
        for i in range(len(candidateNodes)):
            sw = 0
            currentDuration = round(curtask.instructionSize / candidateNodes[i]["resource"].MIPS)

            curCost = 0

            countOfHoursToProvision = int(ceil(currentDuration / self.PERIOD_DURATION))

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
                    countOfHoursToProvision = int(ceil(lack / self.PERIOD_DURATION))
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

                maxCost = 20
                minCost = 0.8

                h2 = ((maxCost - curCost + 1) / (maxCost - minCost + 1))

                p1 = 1
                p2 = 1
                ratio = p1 + p2

                result = ((h1 * p1) + (h2 * p2)) / ratio

                if bad:
                    result = result ** 2

            self.heuristicCache[hc] = result

            probability.append((result ** self.H_RATIO) * (
                    self.pheromone[curtask.matrixid][candidateNodes[i]["instanceId"]] ** self.P_RATIO))
            if probability[i] >= best:
                best = probability[i]
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
        self.pheromone = (1 - self.EVAP_RATIO) * self.pheromone + (self.EVAP_RATIO * 0.04) + 0.001

    def resetProblemNodeList(self):
        problemNodeList = []

        for instance in self.environment._instances.instances:
            tmp = {"PERIOD_DURATION": 3600, "instanceId": instance["instanceId"], "resource": instance["resource"],
                   "currentTask": None,
                   "currentTaskDuration": 0, "totalDuration": 0, "totaltime": 0, "processedTasks": [],
                   "processedTasksIds": set(), "currentStartTime": 0, "instanceFinishTime": 0.0, "totalCost": 0,
                   "instanceStartTime": None, "taskStart": 0}
            problemNodeList.append(tmp)

        return problemNodeList

    def run_ant(self, ant):

        AFT_Dic = {'start': 0}
        for k in range(1, self.environment._graph.nodeNum - 1):
            probability = []
            curTask = self.environment.sortedWorkflowNodes[k]
            candidateNodes = ant.problemNodeList

            # A matrix for finish times for each node
            mx = 0
            for parent in curTask.parents:
                if AFT_Dic[parent.id] > mx:
                    mx = AFT_Dic[parent.id]
            ant.finished[curTask.id] = mx

            bestOptionByProbability = self.calculateHeuristic(candidateNodes, curTask, ant.finished, probability)

            if random.random() < self.Q0:
                dest = candidateNodes[bestOptionByProbability]
            else:
                dest = self.rwsSelection(candidateNodes, probability)

            newTaskDuration = round(curTask.instructionSize / dest["resource"].MIPS)
            countOfHoursToProvision = max(int(ceil(
                (newTaskDuration - max(dest["instanceFinishTime"] - curTask.EST, 0)) / (
                    self.PERIOD_DURATION))), 0)
            addedTimeToProvision = countOfHoursToProvision * self.PERIOD_DURATION

            if dest["currentTask"] is None:
                dest["instanceStartTime"] = ant.finished[curTask.id]
                dest["taskStart"] = ant.finished[curTask.id]
                dest["instanceFinishTime"] = addedTimeToProvision
                dest["currentStartTime"] = round(ant.finished[curTask.id] + newTaskDuration)
                dest["currentTaskDuration"] = newTaskDuration
                dest["totalDuration"] += newTaskDuration
                dest["totaltime"] = countOfHoursToProvision
                dest["currentTask"] = curTask
                dest["totalCost"] += countOfHoursToProvision * dest["resource"].costPerInterval

                if dest["instanceId"] + 1 != self.environment._graph.maxParallel and not dest[
                                                                                             "instanceId"] + 1 >= self.environment._graph.maxParallel * self.environment._resources.size:
                    newinst = {"instanceId": dest["instanceId"] + 1,
                               "resource": dest["resource"], "currentTask": None,
                               "currentTaskDuration": 0, "totalDuration": 0, "totaltime": 0,
                               "processedTasks": [],
                               "processedTasksIds": set(), "currentStartTime": 0, "instanceFinishTime": 0.0,
                               "totalCost": 0,
                               "instanceStartTime": None, "taskStart": 0}
                    ant.problemNodeList.append(newinst)

            else:
                remain = dest["instanceFinishTime"] - dest["totalDuration"]
                countOfHoursToProvision = max(
                    int(round((newTaskDuration - remain) / self.PERIOD_DURATION)), 0)
                addedTimeToProvision = countOfHoursToProvision * self.PERIOD_DURATION
                dest["instanceFinishTime"] += addedTimeToProvision
                dest["taskStart"] = max(ant.finished[curTask.id], dest["currentStartTime"])
                dest["currentStartTime"] = round(dest["taskStart"] + newTaskDuration)
                dest["currentTaskDuration"] = newTaskDuration
                dest["totalDuration"] += newTaskDuration
                dest["totaltime"] += countOfHoursToProvision
                dest["currentTask"] = curTask
                dest["totalCost"] += countOfHoursToProvision * dest["resource"].costPerInterval

            antNode = {"id": curTask.id, "AST": int(round(dest["taskStart"])),
                       "AFT": int(round(dest["taskStart"] + newTaskDuration)), "runTime": newTaskDuration,
                       "selectedInstance": dest["instanceId"], "LFT": curTask.LFT}

            dest["processedTasksIds"].add(curTask.id)

            ant.solution.append(antNode)
            AFT_Dic[curTask.id] = antNode["AFT"]
            # self.probability = []
        return ant

    def schedule(self, environment, deadline):
        self.environment = environment
        # Empty Ant
        empty_ant = structure()
        empty_ant.solution = []
        empty_ant.cost = 0.0
        empty_ant.makeSpan = 0.0
        empty_ant.Utils = 0.0
        empty_ant.problemNodeList = self.environment.problemNodeList
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
        self.pheromone = np.full((self.environment._graph.nodeNum + 2, self.environment._resources.size * self.environment._graph.maxParallel), 0.04)

        # ACO main loop
        for it in range(self.MaxIt):
            # Move Ants
            with ThreadPoolExecutor(max_workers=self.nAnt) as executor:
                futures = [executor.submit(self.run_ant, ant[j]) for j in range(self.nAnt)]
                ants = [future.result() for future in futures]

            for at in ants:
                at.makeSpan = at.solution[-1]["AFT"]
                at.cost, at.Utils = self.getSolutionCost(at.problemNodeList)

                if at.cost < bestAnt.cost and at.makeSpan <= deadline:
                    bestAnt.solution = at.solution
                    bestAnt.cost = at.cost
                    bestAnt.Utils = at.Utils
                    bestAnt.makeSpan = at.makeSpan
                    print("best ant: " + str(bestAnt.cost))

                at.solution = []
                self.localUpdate()
                at.problemNodeList = self.resetProblemNodeList()

            self.updatePheromone(bestAnt)
            return

        return bestAnt

    class HeuristicCondition:

        def __init__(self, curDuration, curCost, curStartTime, instanceId, sd):
            self.__curDuration = curDuration
            self.__curCost = curCost
            self.__curStartTime = curStartTime
            self.__instanceId = instanceId
            self.__sd = sd

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
