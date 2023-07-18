import time
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
        self.nAnt = 10
        self.H_RATIO = 5
        self.P_RATIO = 1
        self.EVAP_RATIO = 0.1
        self.Q0 = 0.8
        self.PERIOD_DURATION = 3600

        self.pheromone = None
        self.environment = None
        self.heuristicCache = []
        self.CacheValues = {}

    def calculateHeuristic(self, candidateNodes, curtask, finished, probability):
        best = -1
        bestIndex = -1
        for i in range(len(candidateNodes)):
            result = 0
            sw = 0
            currentDuration = ceil(curtask.instructionSize / candidateNodes[i]["resource"].MIPS)

            curCost = 0

            countOfHoursToProvision = int(ceil(currentDuration / self.PERIOD_DURATION))

            if len(candidateNodes[i]["processedTasksIds"]) == 0:
                curCost = candidateNodes[i]["resource"].costPerInterval * countOfHoursToProvision
            else:
                if currentDuration <= self.PERIOD_DURATION - candidateNodes[i]["instanceFinishTime"]:
                    curCost = 0
                else:
                    lack = currentDuration - self.PERIOD_DURATION - candidateNodes[i]["instanceFinishTime"]
                    countOfHoursToProvision = int(ceil(lack / self.PERIOD_DURATION))
                    curCost = countOfHoursToProvision * candidateNodes[i]["resource"].costPerInterval

            currentST = max(candidateNodes[i]["instanceFinishTime"], finished[curtask.id])
            currentFT = currentST + currentDuration

            # Cache = str(currentDuration)+str(currentST)+str(candidateNodes[i]["instanceId"])+str(curtask.subDeadline)+str(curCost)
            # Cache = self.HeuristicCondition(currentDuration, curCost, currentST, candidateNodes[i]["instanceId"], curtask.subDeadline)
            # Cache = structure()
            # Cache.duration = currentDuration
            # Cache.ST = currentST
            # Cache.ID = candidateNodes[i]["instanceId"]
            # Cache.deadline = curtask.subDeadline
            # Cache.Cost = curCost

            if not str(curtask.id) == "end" and not str(curtask.id) == "start":
                if currentFT > curtask.LFT:
                    result = 0.0
                    sw = 1

            # if Cache in self.heuristicCache:
            #     result = self.CacheValues[str(currentDuration)+str(currentST)+str(candidateNodes[i]["instanceId"])+str(curtask.subDeadline)+str(curCost)]
            #     sw = 2

            if sw == 0:
                h1 = 0.0
                h2 = 0.0

                bad = False

                if currentFT <= curtask.subDeadline:
                    h1 = 1
                else:
                    h1 = max(0, (((curtask.LFT - currentFT) + 1) / ((curtask.LFT - curtask.subDeadline) + 1)))
                    bad = True

                maxCost = 1.00
                minCost = 0.12

                h2 = ((maxCost - curCost + 1) / (maxCost - minCost + 1))

                p1 = 1
                p2 = 1
                ratio = p1 + p2

                result = ((h1 * p1) + (h2 * p2)) / ratio

                # if bad:
                #     result = result ** 2

            # self.heuristicCache.append(Cache)
            # self.CacheValues[str(currentDuration)+str(currentST)+str(candidateNodes[i]["instanceId"])+str(curtask.subDeadline)+str(curCost)] = result

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

        # return candidates[random.randint(0, len(candidates) + 1)]

    def getSolutionCost(self, tmp):
        usedTime = 0
        totalTime = 0
        result = 0
        for inst in tmp:
            result += inst["totalCost"]
            if inst["totalCost"] != 0:
                usedTime += inst["totalDuration"]
                totalTime += ceil(usedTime / 3600)
        t = usedTime / (totalTime * 3600)
        return result, t

    def updatePheromone(self, bestAnt):
        if bestAnt.cost != 0:
            value = self.EVAP_RATIO * (1 / bestAnt.cost)  + 0.5
            for sol in bestAnt.solution:
                self.pheromone[int(sol["id"].split("ID")[1])][sol["selectedInstance"]] = ((self.pheromone[
                    int(sol["id"].split("ID")[1])][sol["selectedInstance"]]) * (1 - self.EVAP_RATIO)) + value

    def localUpdate(self, lbest):
        for sol in lbest.solution:
            self.pheromone[int(sol["id"].split("ID")[1])][sol["selectedInstance"]] = ((self.pheromone[int(sol["id"].split("ID")[1])][sol["selectedInstance"]]) * (1 - self.EVAP_RATIO)) + (self.EVAP_RATIO * 0.12)

    def resetProblemNodeList(self):
        problemNodeList = []

        for instance in self.environment._instances.instances:
            tmp = {"instanceId": instance["instanceId"], "resource": instance["resource"], "totalDuration": 0,
                   "finishDuration": 0,
                   "processedTasksIds": set(), "currentStartTime": 0, "instanceFinishTime": 0.0, "totalCost": 0}
            problemNodeList.append(tmp)

        return problemNodeList

    def IC_PCP_phase(self, ICPCP):
        value = self.EVAP_RATIO * (1 / ICPCP.cost)  # + 0.09
        for sol in ICPCP.solution.items():
            if sol[0] == "end" or sol[0] == "start":
                continue
            test = int(sol[0].split("ID")[1])
            test2 = sol[1]
            self.pheromone[int(sol[0].split("ID")[1])][sol[1]] = ((self.pheromone[int(sol[0].split("ID")[1])][
                sol[1]]) * (1 - self.EVAP_RATIO)) + value

    def schedule(self, environment, deadline, IC_PCP):
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
        # ant = empty_ant.repeat(self.nAnt)

        # Pheromone Matrix
        self.pheromone = np.full(
            (environment._graph.nodeNum + 1, environment._resources.size * environment._graph.maxParallel), 0.12)

        # # apply the IC_PCP initial pheremone
        # self.IC_PCP_phase(IC_PCP)
        print(IC_PCP)
        # ACO main loop
        for it in range(self.MaxIt):
            # Move Ants
            ant = empty_ant.repeat(self.nAnt)
            with ThreadPoolExecutor(max_workers=self.nAnt) as executor:
                def run_ant(j):
                    total_duration = 0
                    total_time = 0
                    AFT_Dic = {'start': 0}
                    for k in range(1, environment._graph.nodeNum - 1):
                        probability = []
                        curTask = environment.sortedWorkflowNodes[k]
                        candidateNodes = ant[j].problemNodeList

                        # A matrix for finish times for each node
                        mx = 0
                        for parent in curTask.parents:
                            if AFT_Dic[parent.id] > mx:
                                mx = AFT_Dic[parent.id]
                        ant[j].finished[curTask.id] = mx

                        bestOptionByProbability = self.calculateHeuristic(candidateNodes, curTask, ant[j].finished, probability)

                        if random.random() < self.Q0:
                            dest = candidateNodes[bestOptionByProbability]
                        else:
                            dest = self.rwsSelection(candidateNodes, probability)

                        newTaskDuration = ceil(curTask.instructionSize / dest["resource"].MIPS)
                        countOfHoursToProvision = int(ceil((newTaskDuration - (dest["finishDuration"] - dest["totalDuration"])) / self.PERIOD_DURATION))
                        addedTimeToProvision = countOfHoursToProvision * self.PERIOD_DURATION

                        dest["totalDuration"] += newTaskDuration
                        dest["currentStartTime"] = max(ant[j].finished[curTask.id], dest["instanceFinishTime"])
                        dest["finishDuration"] += addedTimeToProvision
                        dest["instanceFinishTime"] = dest["currentStartTime"] + newTaskDuration
                        dest["totalCost"] += countOfHoursToProvision * dest["resource"].costPerInterval
                        ant[j].cost += countOfHoursToProvision * dest["resource"].costPerInterval
                        total_time += addedTimeToProvision
                        total_duration += newTaskDuration

                        if countOfHoursToProvision > 0:
                            if dest["instanceId"] + 1 != environment._graph.maxParallel and not dest[
                                                                                                    "instanceId"] + 1 >= environment._graph.maxParallel * environment._resources.size:
                                newinst = {"instanceId": dest["instanceId"] + 1,
                                           "resource": dest["resource"], "totalDuration": 0, "finishDuration": 0,
                                           "processedTasksIds": set(), "currentStartTime": 0, "instanceFinishTime": 0.0,
                                           "totalCost": 0}
                                ant[j].problemNodeList.append(newinst)

                        antNode = {"id": curTask.id, "AST": dest["currentStartTime"],
                                   "AFT": dest["instanceFinishTime"], "runTime": newTaskDuration,
                                   "selectedInstance": dest["instanceId"], "LFT": curTask.LFT}

                        dest["processedTasksIds"].add(curTask.id)

                        ant[j].solution.append(antNode)
                        AFT_Dic[curTask.id] = antNode["AFT"]

                    ant[j].makeSpan = ant[j].solution[-1]["AFT"]

                    if ant[j].cost < bestAnt.cost and ant[j].makeSpan <= deadline:
                        bestAnt.solution = ant[j].solution
                        bestAnt.cost = ant[j].cost
                        bestAnt.Utils = total_duration / (total_time)
                        bestAnt.makeSpan = ant[j].makeSpan
                        print("best ant: " + str(bestAnt.cost))

                    # ant[j].solution = []
                    self.localUpdate(ant[j])
                    # ant[j].problemNodeList = self.resetProblemNodeList()
                    # ant[j].cost = 0.0

                executor.map(run_ant, range(self.nAnt))

            self.updatePheromone(bestAnt)

        return bestAnt
