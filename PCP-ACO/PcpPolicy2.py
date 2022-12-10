import sys
from WorkflowPolicy import WorkflowPolicy
from Instance import Instance
from WorkflowNode import WorkflowNode
from math import ceil

class PcpPolicy2(WorkflowPolicy):
    def __init__(self, g, rs, bw):
        super().__init__(g, rs, bw)
        self.backCheck = True

    def findCriticalParent(self, child):
        criticalPar = None
        criticalParStart = -1
        curStart = None
        for parentLink in child.getParents():
            parentNode = self._graph.getNodes().get(parentLink.getId())
            if parentNode.isScheduled():
                continue

            curStart = parentNode.getEFT() + round(float(parentLink.getDataSize() / self._bandwidth))
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

    def computeNewESTs(self, path, inst, startTime):
        newESTs = [None] * len(path)
        start = None
        curTime = startTime
        for i in range(len(path)):
            curNode = path[i]
            for parent in curNode.getParents():
                parentNode = self._graph.getNodes().get(parent.getId())
                if parentNode.isScheduled():
                    start = parentNode.getEFT()
                    if parentNode.getSelectedResource() != inst.getId():
                        start += round(float(parent.getDataSize() / self._bandwidth))
                else:
                    if i > 0 and parentNode.getId() == path[i - 1].getId():
                        start = curTime
                    else:
                        start = parentNode.getEFT() + round(float(parent.getDataSize() / self._bandwidth))
                if start > curTime:
                    curTime = start

            newESTs[i] = int(curTime)
            curTime += round(float(curNode.getInstructionSize() / inst.getType().getMIPS()))
        return newESTs

    def computeNewLFTs(self, path, inst, finishTime):
        newLFTs = [None] * len(path)
        finish = None
        curTime = finishTime
        i = len(path) - 1
        while i >= 0:
            curNode = path[i]
            for child in curNode.getChildren():
                childNode = self._graph.getNodes().get(child.getId())
                if childNode.isScheduled():
                    finish = childNode.getLST()
                    if childNode.getSelectedResource() != inst.getId():
                        finish -= round(float(child.getDataSize() / self._bandwidth))
                else:
                    if i < len(path) - 1 and childNode.getId() == path[i + 1].getId():
                        finish = curTime
                    else:
                        finish = childNode.getLST() - round(float(child.getDataSize() / self._bandwidth))
                if finish < curTime:
                    curTime = finish

            newLFTs[i] = int(curTime)
            curTime -= round(float(curNode.getInstructionSize() / inst.getType().getMIPS()))
            i -= 1

        return newLFTs

    def checkInstance(self, path, curInst):
        finishTime = curInst.getFinishTime()
        startTime = curInst.getStartTime()
        interval = self._resources.getInterval()
        curCost = ceil(float(finishTime - startTime) / float(interval)) * curInst.getType().getCost()
        newCost = None
        newESTs = [None] * len(path)
        newLFTs = [None] * len(path)
        success = True
        curTime = 0

        curIntervalFinish = startTime + int(ceil(float(finishTime - startTime) / float(interval)) * interval)
        newESTs = self.computeNewESTs(path, curInst, finishTime)
        tmp = path[len(path) - 1]
        newLFTs = self.computeNewLFTs(path, curInst, tmp.getLFT())
        if newESTs[0] > curIntervalFinish and finishTime != 0:
            success = False
        if finishTime == 0:
            startTime = newESTs[0]
        i = 0
        while i < len(path) and success:
            curNode = path[i]
            curTime = newESTs[i] + round(float(curNode.getInstructionSize() / curInst.getType().getMIPS()))
            # curNode.setAFT(curTime)
            if curTime > newLFTs[i]:
                success = False
            i += 1

        if success:
            newCost = ceil(
                (float(curTime - startTime)) / float(self._resources.getInterval())) * curInst.getType().getCost()
            newCost -= curCost
            return float(newCost)

        if not self.backCheck:
            return sys.maxsize

        curIntervalStart = finishTime - int(ceil((float(finishTime - startTime)) / float(interval)) * interval)
        newLFTs = self.computeNewLFTs(path, curInst, startTime)
        newESTs = self.computeNewESTs(path, curInst, path[0].getEST())
        if newLFTs[len(path) - 1] > curIntervalStart:
            success = True
        else:
            success = False
        i = len(path) - 1
        while i >= 0 and success:
            curNode = path[i]
            curTime = newLFTs[i] - round(float(curNode.getInstructionSize()) / curInst.getType().getMIPS())
            if curTime < newESTs[i]:
                success = False
            i -= 1
        if success:
            newCost = ceil(
                float(finishTime - curTime) / float(self._resources.getInterval())) * curInst.getType().getCost()
            newCost -= curCost
            return float(newCost)
        return sys.maxsize

    def setInstance(self, path, curInst):
        finishTime = curInst.getFinishTime()
        startTime = curInst.getStartTime()
        newESTs = [None] * len(path)
        newLFTs = [None] * len(path)
        success = True
        curTime = 0
        curRuntime = None
        firstStart = path[0].getEST()
        lastFinish = path[len(path) - 1].getLFT()

        newESTs = self.computeNewESTs(path, curInst, finishTime)
        newLFTs = self.computeNewLFTs(path, curInst, lastFinish)
        i = 0
        while i < len(path) and success:
            curNode = path[i]
            curRuntime = round(float(curNode.getInstructionSize()) / curInst.getType().getMIPS())
            curTime = newESTs[i] + curRuntime
            if curTime > newLFTs[i]:
                success = False

            curNode.setEST(newESTs[i])
            curNode.setEFT(int(curTime))

            curNode.setLFT(newLFTs[i])
            curNode.setLST(int((newLFTs[i] - curRuntime)))

            curNode.setRunTime(int(curRuntime))
            curNode.setSelectedResource(curInst.getType().getId())
            curNode.setScheduled()
            i += 1

        if success:
            if curInst.getFinishTime() == 0:
                curInst.setStartTime(path[0].getEST())
                curInst.setFirstTask(path[0].getId())

            curInst.setFinishTime(path[len(path) - 1].getLFT())
            curInst.setLastTask(path[len(path) - 1].getId())
            return
        else:
            for i in range(len(path)):
                path[i].setUnscheduled()

        if not self.backCheck:
            return

        newLFTs = self.computeNewLFTs(path, curInst, startTime)
        newESTs = self.computeNewESTs(path, curInst, firstStart)
        success = True
        i = len(path) - 1
        while i >= 0 and success:
            curNode = path[i]
            curRuntime = round(float(curNode.getInstructionSize()) / curInst.getType().getMIPS())
            curTime = newLFTs[i] - curRuntime
            if curTime < newESTs[i]:
                success = False

            curNode.setLFT(newLFTs[i])
            curNode.setLST(int(curTime))

            curNode.setEST(newESTs[i])
            curNode.setEFT(int((newESTs[i] + curRuntime)))

            curNode.setRunTime(int(curRuntime))
            curNode.setSelectedResource(curInst.getId())
            curNode.setScheduled()
            i -= 1

        if curInst.getFinishTime() == 0:
            curInst.setFinishTime(path[len(path) - 1].getLFT())
            curInst.setLastTask(path[len(path) - 1].getId())

        curInst.setStartTime(path[0].getEST())
        curInst.setFirstTask(path[0].getId())

    def assignPath(self, path):
        cost = None
        bestCost = sys.maxsize
        bestInst = -1

        # check in the current instances that we reserved
        for curInst in range(self._instances.getSize()):
            cost = self.checkInstance(path, self._instances.getInstance(curInst))
            if cost < bestCost:
                bestCost = cost
                bestInst = curInst

        # we came from the most expensive one to the cheapest one [20,...,0.8]
        curRes = 0
        # launch a new instance
        while curRes < self._resources.getSize():
            inst = Instance(self._instances.getSize(), self._resources.getResource(curRes))
            cost = self.checkInstance(path, inst)
            if cost < bestCost:
                bestCost = cost
                bestInst = 10000 + curRes
            curRes += 1

        if bestInst < 10000:
            self.setInstance(path, self._instances.getInstance(bestInst))
        else:
            bestInst -= 10000
            inst = Instance(self._instances.getSize(), self._resources.getResource(bestInst))
            self._instances.addInstance(inst)
            self.setInstance(path, inst)

    def updateParentsLFT(self, childNode):
        for parent in childNode.getParents():
            parentNode = self._graph.getNodes()
            parentNode = parentNode[parent.getId()]
            newLFT = None

            if childNode.isScheduled():
                newLFT = childNode.getLST()
                if not parentNode.isScheduled() or parentNode.getSelectedResource() != childNode.getSelectedResource():
                    newLFT -= round(float(parent.getDataSize()) / self._bandwidth)

            else:
                newLFT = childNode.getLST() - round(float(parent.getDataSize()) / self._bandwidth)
            if parentNode.getLFT() > newLFT:
                parentNode.setLFT(newLFT)
                parentNode.setLST(int(newLFT - round(parentNode.getRunTime())))

                if parentNode.getLFT() < parentNode.getEFT():
                    print(
                        "LFT Setting: Id=" + parentNode.getId() + " EFT=" + str(parentNode.getEFT()) + " LFT=" + str(parentNode.getLFT()))

                self.updateParentsLFT(parentNode)

    def updateChildrenEST(self, parentNode):
        for child in parentNode.getChildren():
            childNode = self._graph.getNodes().get(child.getId())
            newEST = None

            if parentNode.isScheduled():
                newEST = parentNode.getEFT()
                if not childNode.isScheduled() or parentNode.getSelectedResource() != childNode.getSelectedResource():
                    newEST += round(float(child.getDataSize()) / self._bandwidth)

            else:
                newEST = parentNode.getEFT()
            if childNode.getEST() < newEST:
                childNode.setEST(newEST)
                childNode.setEFT(int(newEST + round(childNode.getRunTime())))

                if childNode.getLFT() < childNode.getEFT():
                    print(
                        "EST Setting: ID=" + childNode.getId() + " EFT=" + childNode.getEFT() + " LFT=" + childNode.getLFT())

                self.updateChildrenEST(childNode)

    def setEndNodeEST(self):
        endTime = -1
        endNode = self._graph.getNodes()
        endNode = endNode[self._graph.getEndId()]

        for parent in endNode.getParents():
            curEndTime = self._graph.getNodes()
            curEndTime = curEndTime[parent.getId()].getEFT()
            if endTime < curEndTime:
                endTime = curEndTime
        endNode.setEST(endTime)
        endNode.setEFT(endTime)

    # algorithm 2 in the paper
    def assignParents(self, curNode):
        criticalPath = []

        criticalPath = self.findPartialCriticalPath(curNode)
        if not criticalPath:
            return

        self.assignPath(criticalPath)
        for i in range(len(criticalPath)):
            self.updateChildrenEST(criticalPath[i])
            self.updateParentsLFT(criticalPath[i])

        for i in range(len(criticalPath)):
            self.assignParents(criticalPath[i])

        self.assignParents(curNode)

    def schedule(self, startTime, deadline):
        cost = None

        self.setRuntimes()
        self.computeESTandEFT(startTime)
        self.computeLSTandLFT(deadline)
        self.initializeStartEndNodes(startTime, deadline)

        self.assignParents(self._graph.getNodes().get(self._graph.getEndId()))

        self.setEndNodeEST()
        cost = super().computeFinalCost()
        return cost
