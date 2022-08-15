import sys

sys.path.append('/Users/apple/Desktop/Create WS-ACO/MyCode')
from IaaSCloudWorkflowScheduler.WorkflowPolicy import WorkflowPolicy
from IaaSCloudWorkflowScheduler.Instance import Instance
from IaaSCloudWorkflowScheduler.WorkflowNode import WorkflowNode
from math import ceil, floor


class PcpD2Policy2(WorkflowPolicy):
    def __init__(self, g, rs, bw):
        super().__init__(g, rs, bw)

    class result:
        cost = None
        finishTime = None

    class PriorityQueue(object):
        def __init__(self):
            self.queue = []

        def __str__(self):
            return ' '.join([str(i) for i in self.queue])

        def isEmpty(self):
            return len(self.queue) == 0

        def insert(self, data):
            self.queue.append(data)

        def remove(self):  # check for time complexity !!!
            try:
                max = 0
                for i in range(len(self.queue)):
                    if self.queue[i].getUpRank() > self.queue[max].getUpRank():
                        max = i
                item = self.queue[max]
                del self.queue[max]
                return item
            except IndexError:
                print('Error !!!')
                exit()

    def findCriticalParent(self, child):
        criticalPar = None
        criticalParStart = -1
        curStart = None

        for parentLink in child.getParents():
            parentNode = self._graph.getNodes().get(parentLink.getId())
            if parentNode.isScheduled():
                continue

            curStart = parentNode.getEFT() + round(float(parentLink.getDataSize()) / self._bandwidth)
            if curStart > criticalParStart:
                criticalParStart = curStart
                criticalPar = parentNode

        return criticalPar

    def findPartialCriticalPath(self, curNode):
        criticalPath = []

        while True:
            curNode = self.findCriticalParent(curNode)
            if curNode is not None:
                criticalPath.insert(0, curNode)
            if curNode is None:
                break

        return criticalPath

    def assignPath(self, path):
        # last = self._graph.getNodes().get(self._graph.getEndId())
        last = len(path) - 1
        pathEST = path[0].getEST()
        pathEFT = path[last].getEFT()
        # pathEFT = last.getEFT()
        PSD = path[last].getLFT() - pathEST
        # PSD = last.getLFT() - pathEST
        i = 0
        while i <= len(path) - 1:
            curNode = path[i]
            ########################
            subDeadline = pathEST + int(floor(float(curNode.getEFT() - pathEST) / float(pathEFT - pathEST) * PSD))

            curNode.setDeadline(subDeadline)
            curNode.setScheduled()

            if i > 0:
                newEST = path[i - 1].getDeadline() + round(
                    float(self.getDataSize(path[i - 1], curNode)) / self._bandwidth)
                if newEST > curNode.getEST():
                    curNode.setEST(newEST)
                    curNode.setEFT(newEST + curNode.getRunTime())
            i += 1

    def updateChildrenEST(self, parentNode):
        for child in parentNode.getChildren():
            childNode = self._graph.getNodes().get(child.getId())
            newEST = None

            if not childNode.isScheduled():
                if parentNode.isScheduled():
                    newEST = parentNode.getDeadline() + round(float(child.getDataSize() / self._bandwidth))
                else:
                    newEST = parentNode.getEFT() + round(float(child.getDataSize()) / self._bandwidth)

                if childNode.getEST() < newEST:
                    childNode.setEST(newEST)
                    childNode.setEFT(int(newEST + round(childNode.getRunTime())))
                    self.updateChildrenEST(childNode)

    def updateParentsLFT(self, childNode):
        for parent in childNode.getParents():
            parentNode = self._graph.getNodes().get(parent.getId())
            newLFT = None

            if not parentNode.isScheduled():
                if childNode.isScheduled():
                    newLFT = round(childNode.getEST() - float(parent.getDataSize()) / self._bandwidth)
                else:
                    newLFT = round(childNode.getLST() - float(parent.getDataSize()) / self._bandwidth)

                if parentNode.getLFT() > newLFT:
                    parentNode.setLFT(newLFT)
                    parentNode.setLST(int(newLFT - round(parentNode.getRunTime())))
                    self.updateParentsLFT(parentNode)

    def assignParents(self, curNode):
        criticalPath = []

        criticalPath = self.findPartialCriticalPath(curNode)
        if not criticalPath:
            return

        self.assignPath(criticalPath)
        for i in range(len(criticalPath)):
            self.updateChildrenEST(criticalPath[i])
            self.updateParentsLFT(criticalPath[i])
            self.assignParents(criticalPath[i])

        # for i in range(len(criticalPath)):
        #     self.assignParents(criticalPath[i])

        self.assignParents(curNode)

    def distributeDeadline(self):
        self.assignParents(self._graph.getNodes().get(self._graph.getEndId()))
        # je suis ici
        self._graph.getNodes().get(self._graph.getEndId()).setDeadline(0)
        for node in self._graph.getNodes().values():
            node.setUnscheduled()

    def checkInstance(self, curNode, curInst):
        finishTime = curInst.getFinishTime()
        startTime = curInst.getStartTime()
        interval = self._resources.getInterval()
        curCost = ceil(float(finishTime - startTime) / float(interval)) * curInst.getType().getCost()
        curIntervalFinish = startTime + int(ceil(float(finishTime - startTime) / float(interval)) * interval)
        start = None
        curStart = int(finishTime)
        curFinish = None

        for parent in curNode.getParents():
            parentNode = self._graph.getNodes().get(parent.getId())

            start = parentNode.getEFT()
            if parentNode.getSelectedResource() != curInst.getId():
                start += round(float(parent.getDataSize()) / self._bandwidth)
            if start > curStart:
                curStart = start

        if finishTime == 0:
            startTime = curStart

        r = self.result()
        curFinish = int(curStart + round(float(curNode.getInstructionSize()) / curInst.getType().getMIPS()))
        r.finishTime = curFinish
        if (finishTime != 0 and curStart > curIntervalFinish) or curFinish > curNode.getDeadline():
            r.cost = sys.maxsize
        else:
            r.cost = float(ceil(float(curFinish - startTime) / float(interval)) * curInst.getType().getCost() - curCost)

        return r

    def setInstance(self, curNode, curInst):
        start = None
        curStart = int(curInst.getFinishTime())
        curFinish = None

        for parent in curNode.getParents():
            parentNode = self._graph.getNodes().get(parent.getId())

            start = parentNode.getEFT()
            if parentNode.getSelectedResource() != curInst.getId():
                start += round(float(parent.getDataSize()) / self._bandwidth)
            if start > curStart:
                curStart = start

        curFinish = curStart + round(float(curNode.getInstructionSize()) / curInst.getType().getMIPS())
        curNode.setEST(curStart)
        curNode.setEFT(curFinish)
        curNode.setSelectedResource(curInst.getType().getId())
        curNode.setScheduled()

        if curInst.getFinishTime() == 0:
            curInst.setStartTime(curStart)
            curInst.setFirstTask(curNode.getId())

        curInst.setFinishTime(curFinish)
        curInst.setLastTask(curNode.getId())

    def planning(self):
        queue = self.PriorityQueue()
        r = self.result()
        bestFinish = sys.maxsize

        self.computeUpRank()
        for node in self._graph.nodes.values():
            if not node.getId() == self._graph.getStartId() and not node.getId() == self._graph.getEndId():
                queue.insert(node)

        while not queue.isEmpty():
            curNode = queue.remove()
            bestInst = -1
            bestCost = sys.maxsize

            for curInst in range(self._instances.getSize()):
                r = self.checkInstance(curNode, self._instances.getInstance(curInst))
                if r.cost < bestCost:
                    bestCost = r.cost
                    bestFinish = r.finishTime
                    bestInst = curInst
                elif bestCost < sys.maxsize and r.cost == bestCost and r.finishTime < bestFinish:
                    bestFinish = r.finishTime
                    bestInst = curInst

            curRes = self._resources.getSize() - 1
            # because the cheapest one is the last
            while curRes >= 0:
                inst = Instance(self._instances.getSize(), self._resources.getResource(curRes))
                r = self.checkInstance(curNode, inst)
                if r.cost < bestCost:
                    bestCost = r.cost
                    bestFinish = r.finishTime
                    bestInst = 10000 + curRes
                elif bestCost < sys.maxsize and r.cost == bestCost and r.finishTime < bestFinish:
                    bestFinish = r.finishTime
                    bestInst = 10000 + curRes
                curRes -= 1

            if bestInst < 10000:
                self.setInstance(curNode, self._instances.getInstance(bestInst))
            else:
                bestInst -= 10000
                inst = Instance(self._instances.getSize(), self._resources.getResource(bestInst))
                self._instances.addInstance(inst)
                self.setInstance(curNode, inst)

    def setEndNodeEST(self):
        endTime = -1
        endNode = self._graph.getNodes().get(self._graph.getEndId())

        for parent in endNode.getParents():
            curEndTime = self._graph.getNodes().get(parent.getId()).getEFT()
            if endTime < curEndTime:
                endTime = curEndTime

        endNode.setEST(endTime)
        endNode.setEFT(endTime)

    def schedule(self, startTime, deadline):
        cost = None

        self.setRuntimes()
        self.computeESTandEFT(startTime)
        self.computeLSTandLFT(deadline)
        self.initializeStartEndNodes(startTime, deadline)

        self.distributeDeadline()
        self.planning()

        self.setEndNodeEST()
        cost = super().computeFinalCost()
        return cost
