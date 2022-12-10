from math import ceil
from queue import Queue
from IaaSCloudWorkflowScheduler.Constants import Constants
# from ..Constants import Constants


class CloudAcoResourceInstance:
    def __init__(self, resource, id=None):
        self.__PERIOD_DURATION = 3600
        self.__instanceId = id
        self.__resource = resource
        self.__currentTask = None
        self.__currentTaskDuration = 0
        self.__processedTasks = []
        self.__processedTasksIds = set()
        self.__currentStartTime = 0
        self.__instanceFinishTime = 0.0
        self.__totalCost = 0
        self.__instanceStartTime = None

    def getPTI(self):
        return len(self.__processedTasksIds)

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
        return round(runtime + self.getBandwidthDuration(node))

    def getInstanceRemainingTime(self, time):
        return max(self.__instanceFinishTime - time, 0)

    def getNewStartTime(self, node, env):
        max_AFT = 0
        for parent in node.getParents():
            parentNode = env.getProblemGraph().getGraph().getNodes().get(parent.getId())
            if parentNode.getAFT() >= max_AFT:
                max_AFT = parentNode.getAFT() + self.getBandwidthDuration(node)
        return round(max_AFT)

    def getInstanceReleaseTime(self):
        return self.__currentStartTime + self.__currentTaskDuration

    def setCurrentTask(self, cloudAcoProblemNode, env, curt):
        node = curt
        if str(node.getId()).lower() == "start" or str(
                node.getId()).lower() == "end":  # i personally think that end is missing here becouse like start end is not allowed to be set !
            return

        newTaskDuration = self.getTaskDuration(node)
        countOfHoursToProvision = max(
            int(ceil(
                (newTaskDuration - self.getInstanceRemainingTime(node.getEST())) / (self.__PERIOD_DURATION * 1.0))),
            0)
        addedTimeToProvision = (countOfHoursToProvision * self.__PERIOD_DURATION)

        if self.__currentTask is None:
            self.__instanceStartTime = max(self.getNewStartTime(node, env), 0)  # node.getEST()
            self.__instanceFinishTime = addedTimeToProvision
            self.__currentStartTime = max(self.getNewStartTime(node, env), 0)
            self.__currentTaskDuration = newTaskDuration
            self.__currentTask = node
            self.__totalCost += countOfHoursToProvision * self.__resource.getCost()
            # if cloudAcoProblemNode.getInstanceId() == 192:
            #     print("first")
            # if cloudAcoProblemNode.getInstanceId() == 194:
            #     print("22222")
            # if cloudAcoProblemNode.getInstanceId() == 196:
            #     print("333333")

            if cloudAcoProblemNode.getInstanceId()+1 != env.getProblemGraph().getGraph().getMaxParallel() and not cloudAcoProblemNode.getInstanceId()+1 >= env.getProblemGraph().getGraph().getMaxParallel() * env.getProblemGraph().getResourceSet().getSize():
                tmp = CloudAcoResourceInstance(cloudAcoProblemNode.getResource(), cloudAcoProblemNode.getInstanceId()+1)
                env.getProblemGraph().getProblemNodeList().append(tmp)

        else:
            remain = self.getInstanceRemainingTime(self.getInstanceReleaseTime())
            countOfHoursToProvision = max(int(round((newTaskDuration - remain) / float(self.__PERIOD_DURATION))), 0)
            addedTimeToProvision = (countOfHoursToProvision * self.__PERIOD_DURATION)
            self.__instanceFinishTime += addedTimeToProvision
            self.__currentStartTime = max(self.getNewStartTime(node, env), self.__currentTask.getAFT())       # it shoudn't be last node.AFT ??
            # self.__currentStartTime = max(int(self.getInstanceReleaseTime()), node.getEST())  # for id05  is (15, 21)
            self.__currentTaskDuration = newTaskDuration
            self.__currentTask = node
            self.__totalCost += countOfHoursToProvision * self.__resource.getCost()

        node.setAST(int(round(self.__currentStartTime)))
        node.setAFT(int(round(self.__currentStartTime + newTaskDuration)))
        node.setRunTime(newTaskDuration)
        node.setSelectedResource(self)
        node.setSelectedInstance(self.__instanceId)
        # node.setSelectedResource(self.getId())

        node.setScheduled()
        self.__processedTasks.append(node)
        self.__processedTasksIds.add(node.getId())

    def getTotalCost(self):
        return self.__totalCost

    def getCost(self, node):
        newTaskDuration = self.getTaskDuration(node)
        countOfHoursToProvision = int(ceil(newTaskDuration / float(self.__PERIOD_DURATION)))

        if countOfHoursToProvision == 0:  # we don't need this becouse it's alwayes 1 at Least
            countOfHoursToProvision = 1
        # not started yet!
        if self.__currentTask is None:
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
        self.__processedTasks = []
        self.__currentStartTime = 0
        self.__processedTasksIds.clear()

    def getInstanceFinishTime(self):
        return self.__instanceFinishTime
