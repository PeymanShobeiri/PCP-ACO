from math import ceil
from queue import Queue
from ..Constants import Constants


class CloudAcoResourceInstance:
    def __init__(self, resource, id=None):
        self.__PERIOD_DURATION = 3600
        self.__instanceId = id
        self.__resource = resource
        self.__currentTask = None
        self.__currentTaskDuration = 0
        self.__processedTasks = Queue()
        self.__processedTasksIds = set()
        self.__currentStartTime = 0  # none or 0 ??
        self.__instanceFinishTime = 0.0
        self.__totalCost = 0
        self.__instanceStartTime = None

    def getResource(self):
        return self.__resource

    def getInstanceId(self):
        return self.__instanceId

    def setInstanceId(self, instanceId):
        self.__instanceId = instanceId

    def getId(self):
        return self.__resource.getId()

    def getInstanceStartTime(self):
        return self.__instanceStartTime

    def getMIPS(self):
        return self.__resource.getMIPS()

    def getBandwidthDuration(self, node):
        duration = 0
        for parent in node.getParents():
            if not parent.getId() in self.__processedTasksIds:
                tt = float(parent.getDataSize()) / (Constants.BANDWIDTH * 1.0)
                if tt > duration:
                    duration = tt

        return duration

    def getTaskDuration(self, node):
        runtime = round(float(node.getInstructionSize()) / self.getMIPS())
        runtime + self.getBandwidthDuration(node)
        return runtime

    def getInstanceRemainingTime(self, time):
        return max(self.__instanceFinishTime - time, 0)

    def getInstanceReleaseTime(self):
        return self.__currentStartTime + self.__currentTaskDuration

    def setCurrentTask(self, cloudAcoProblemNode):
        node = cloudAcoProblemNode.getNode()
        if str(node.getId()).lower() == "start":
            return

        newTaskDuration = self.getTaskDuration(node)
        countOfHoursToProvision = max(
            int(ceil((newTaskDuration - self.getInstanceRemainingTime(node.getEST())) / (self.__PERIOD_DURATION * 1.0))),
            0)
        addedTimeToProvision = (countOfHoursToProvision * self.__PERIOD_DURATION)

        if self.__currentTask == None:
            self.__instanceStartTime = node.getEST()
            self.__instanceFinishTime = addedTimeToProvision
            self.__currentStartTime = node.getEST()
            self.__currentTaskDuration = newTaskDuration
            self.__currentTask = node
            self.__totalCost += countOfHoursToProvision * self.__resource.getCost()
        else:
            remain = self.getInstanceRemainingTime(self.getInstanceReleaseTime())
            countOfHoursToProvision = max(int(round((newTaskDuration - remain) / float(self.__PERIOD_DURATION))), 0)
            addedTimeToProvision = (countOfHoursToProvision * self.__PERIOD_DURATION)
            self.__instanceFinishTime += addedTimeToProvision
            self.__currentStartTime = max(int(self.getInstanceReleaseTime()), node.getEST())
            self.__currentTaskDuration = newTaskDuration
            self.__currentTask = node
            self.__totalCost += countOfHoursToProvision * self.__resource.getCost()
        node.setAST(int(round(self.__currentStartTime)))
        node.setAFT(int(round(self.__currentStartTime + self.__currentTaskDuration)))
        node.setRunTime(newTaskDuration)
        node.setScheduled()
        self.__processedTasks.put(node)

    def getBandwidthDuration(self, node):
        duration = 0
        for parent in node.getParents():
            if not parent.getId() in self.__processedTasksIds:
                tt = float(parent.getDataSize()) / (Constants.BANDWIDTH * 1.0)
                if tt > duration:
                    duration = tt

        return duration

    def getTotalCost(self):
        return self.__totalCost

    def getCost(self, node):
        newTaskDuration = self.getTaskDuration(node)
        countOfHoursToProvision = int(ceil(newTaskDuration / float(self.__PERIOD_DURATION)))

        if countOfHoursToProvision == 0:
            countOfHoursToProvision = 1
        # not started yet!
        if self.__currentTask == None:
            return self.getResource().getCost() * countOfHoursToProvision
        else:
            if newTaskDuration <= self.getInstanceRemainingTime(self.getInstanceReleaseTime()):
                return 0
            else:
                lack = newTaskDuration - self.getInstanceRemainingTime(self.getInstanceReleaseTime())
                countOfHoursToProvision = int(ceil(lack / float(self.__PERIOD_DURATION)))
                return countOfHoursToProvision * self.__resource.getCost()

    def reset(self):
        self.__totalCost = 0
        self.__instanceStartTime = 0
        self.__currentTask = None
        self.__currentTaskDuration = 0
        self.__instanceFinishTime = 0
        self.__processedTasks = Queue()
        self.__currentStartTime = 0
        self.__processedTasksIds.clear()

    def getInstanceFinishTime(self):
        return self.__instanceFinishTime
