from math import ceil
from queue import Queue
from Constants import Constants
from ypstruct import structure


class CloudAcoResourceInstance:
    def __init__(self, resource, id=None):
        self.PERIOD_DURATION = 3600
        self.instanceId = id
        self.resource = resource
        self.currentTask = None
        self.currentTaskDuration = 0
        self.totalDuration = 0
        self.totaltime = 0
        self.processedTasks = []
        self.processedTasksIds = set()
        self.currentStartTime = 0
        self.instanceFinishTime = 0.0
        self.totalCost = 0
        self.instanceStartTime = None

    def getPTI(self):
        return len(self.processedTasksIds)

    def getPeriod(self):
        return self.PERIOD_DURATION

    def getResource(self):
        return self.resource

    def getInstanceId(self):
        return self.instanceId

    def setInstanceId(self, instanceId):
        self.instanceId = instanceId

    def getId(self):
        return self.resource.getId()

    def getInstanceStartTime(self):
        return self.instanceStartTime

    def getMIPS(self):
        return self.resource.getMIPS()

    def getBandwidthDuration(self, node):
        duration = 0
        for parent in node.getParents():
            if not parent.getId() in self.processedTasksIds:
                tt = float(parent.getDataSize()) / (Constants.BANDWIDTH * 1.0)
                if tt > duration:
                    duration = tt

        return duration

    def getTaskDuration(self, node):
        runtime = round(float(node.getInstructionSize()) / self.getMIPS())
        return round(runtime + self.getBandwidthDuration(node))

    def getInstanceRemainingTime(self, time):
        return max(self.instanceFinishTime - time, 0)

    def getNewStartTime(self, node, env):
        max_AFT = 0
        for parent in node.getParents():
            parentNode = env._graph.nodes.get(parent.getId())
            if parentNode.getAFT() >= max_AFT:
                max_AFT = parentNode.getAFT() + self.getBandwidthDuration(node)
        return round(max_AFT)

    def getInstanceReleaseTime(self):
        return self.currentStartTime + self.currentTaskDuration

    def setCurrentTask(self, cloudAcoProblemNode, env, curt):
        out = structure()
        out.sw = 0
        node = curt
        if str(node.getId()).lower() == "start" or str(
                node.getId()).lower() == "end":
            return

        newTaskDuration = self.getTaskDuration(node)
        countOfHoursToProvision = max(
            int(ceil((newTaskDuration - self.getInstanceRemainingTime(node.getEST())) / (self.PERIOD_DURATION * 1.0))),
            0)
        addedTimeToProvision = (countOfHoursToProvision * self.PERIOD_DURATION)

        if self.currentTask is None:
            self.instanceStartTime = max(self.getNewStartTime(node, env), 0)
            self.instanceFinishTime = addedTimeToProvision
            self.currentStartTime = max(self.getNewStartTime(node, env), 0)
            self.currentTaskDuration = newTaskDuration
            self.totalDuration += newTaskDuration
            self.totaltime = countOfHoursToProvision
            self.currentTask = node
            self.totalCost += countOfHoursToProvision * self.resource.getCost()

            if cloudAcoProblemNode.instanceId + 1 != env._graph.maxParallel and not cloudAcoProblemNode.getInstanceId() + 1 >= env._graph.maxParallel * env._resources.size:
                newinst = CloudAcoResourceInstance(cloudAcoProblemNode.getResource(), cloudAcoProblemNode.getInstanceId() + 1)
                env.problemNodeList.append(newinst)
                out.newinst = newinst
                out.sw = 1

        else:
            remain = self.getInstanceRemainingTime(self.getInstanceReleaseTime())
            countOfHoursToProvision = max(int(round((newTaskDuration - remain) / float(self.PERIOD_DURATION))), 0)
            addedTimeToProvision = (countOfHoursToProvision * self.PERIOD_DURATION)
            self.instanceFinishTime += addedTimeToProvision
            self.currentStartTime = max(self.getNewStartTime(node, env),
                                        self.currentTask.getAFT())  # it shoudn't be last node.AFT ??
            # self.currentStartTime = max(int(self.getInstanceReleaseTime()), node.getEST())  # for id05  is (15, 21)
            self.currentTaskDuration = newTaskDuration
            self.totalDuration += newTaskDuration
            self.totaltime += countOfHoursToProvision
            self.currentTask = node
            self.totalCost += countOfHoursToProvision * self.resource.getCost()

        node.setAST(int(round(self.currentStartTime)))
        node.setAFT(int(round(self.currentStartTime + newTaskDuration)))
        node.setRunTime(newTaskDuration)
        node.setSelectedResource(self)
        node.setSelectedInstance(self.instanceId)
        # node.setSelectedResource(self.getId())

        node.setScheduled()
        self.processedTasks.append(node)
        self.processedTasksIds.add(node.getId())
        return out

    def getTotalCost(self):
        return self.totalCost

    def getCost(self, node):
        newTaskDuration = self.getTaskDuration(node)
        countOfHoursToProvision = int(ceil(newTaskDuration / float(self.PERIOD_DURATION)))

        if countOfHoursToProvision == 0:  # we don't need this becouse it's alwayes 1 at Least
            countOfHoursToProvision = 1
        # not started yet!
        if self.currentTask is None:
            return self.getResource().getCost() * countOfHoursToProvision
        else:
            if newTaskDuration <= self.getInstanceRemainingTime(self.getInstanceReleaseTime()):
                return 0
            else:
                lack = newTaskDuration - self.getInstanceRemainingTime(self.getInstanceReleaseTime())
                countOfHoursToProvision = int(ceil(lack / float(self.PERIOD_DURATION)))
                return countOfHoursToProvision * self.resource.getCost()

    def reset(self):
        self.totalCost = 0
        self.totalDuration = 0
        self.instanceStartTime = 0
        self.currentTask = None
        self.currentTaskDuration = 0
        self.instanceFinishTime = 0
        self.processedTasks = []
        self.currentStartTime = 0
        self.processedTasksIds.clear()

    def getInstanceFinishTime(self):
        return self.instanceFinishTime
