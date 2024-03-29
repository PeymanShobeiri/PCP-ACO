from InstanceSet import InstanceSet
import sys
from queue import Queue
from WorkflowNode import WorkflowNode
from math import ceil, floor


class WorkflowPolicy:
    def __init__(self, g, rs, bw):
        self._graph = g
        self._resources = rs
        self._instances = []
        self._bandwidth = bw

    def setRuntimes(self):
        maxMIPS = self._resources.getMaxMIPS()
        for node in self._graph.getNodes().values():
            node.setRunTime(ceil(node.getInstructionSize() / maxMIPS))

    def computeLSTandLFT(self, deadline):
        candidateNodes = Queue()
        nodes = self._graph.getNodes()
        curNode = None
        parentNode = None
        childNode = None

        curNode = nodes[self._graph.getEndId()]
        curNode.setLFT(deadline)
        curNode.setLST(deadline)
        # curNode.setAFT(deadline)
        # curNode.setAST(deadline)
        curNode.setScheduled()
        for parent in curNode.getParents():
            candidateNodes.put(parent.getId())

        while not candidateNodes.empty():
            curNode = nodes.get(candidateNodes.get())
            minTime = sys.maxsize
            for child in curNode.getChildren():
                childNode = nodes.get(child.getId())
                # x = (childNode.getLFT() - childNode.getRunTime()) - float(child.getDataSize() / self._bandwidth)
                # thisTime = round((childNode.getLFT() - childNode.getRunTime()) - float(child.getDataSize() / self._bandwidth))

                thisTime = childNode.getLFT() - childNode.getRunTime()
                thisTime -= round(float(child.getDataSize() / self._bandwidth))
                if thisTime < minTime:
                    minTime = thisTime

            curNode.setLFT(int(minTime))
            curNode.setLST(int(minTime - round(curNode.getRunTime())))
            curNode.setScheduled()
            for parent in curNode.getParents():
                isCandidate = True
                parentNode = nodes.get(parent.getId())
                for child in parentNode.getChildren():
                    if not nodes.get(child.getId()).isScheduled():
                        isCandidate = False
                if isCandidate:
                    candidateNodes.put(parent.getId())

        for node in nodes.values():
            node.setUnscheduled()

    def FindMaxParallel(self):
        nodes = self._graph.getNodes()
        levels = dict()
        for node in nodes.values():
            if node.getDAG_level() not in levels:
                levels[node.getDAG_level()] = 1
            else:
                levels[node.getDAG_level()] += 1
        return int((max(levels.values())))

    def computeESTandEFT(self, startTime):
        candidateNodes = Queue()
        nodes = self._graph.getNodes()
        curNode = None
        parentNode = None
        childNode = None
        level = 1

        for node in nodes.values():
            node.setUnscheduled()

        curNode = nodes.get(self._graph.getStartId())
        curNode.setEST(startTime)
        curNode.setEFT(startTime)
        curNode.setDAG_level(0)
        curNode.setScheduled()
        for child in curNode.getChildren():
            candidateNodes.put(child.getId())
            nodes[child.getId()].setDAG_level(level)

        while not candidateNodes.empty():
            thisTime = 0.0
            maxTime = 0.0
            curNode = nodes.get(candidateNodes.get())
            maxTime = -1
            for parent in curNode.getParents():
                parentNode = nodes.get(parent.getId())
                thisTime = round(parentNode.getEFT() + round(parent.getDataSize() / self._bandwidth))
                if thisTime > maxTime:
                    maxTime = thisTime

            curNode.setEST(int(maxTime))
            curNode.setEFT(int(maxTime + round(curNode.getRunTime())))
            curNode.setScheduled()

            for child in curNode.getChildren():
                isCandidate = True
                childNode = nodes.get(child.getId())
                for parent in childNode.getParents():
                    if not nodes.get(parent.getId()).isScheduled():
                        isCandidate = False
                if isCandidate:
                    candidateNodes.put(child.getId())
                    nodes[child.getId()].setDAG_level(curNode.getDAG_level() + 1)

        for node in nodes.values():
            node.setUnscheduled()

    def computeUpRank(self):
        candidateNodes = Queue()
        nodes = self._graph.getNodes()
        curNode = None
        parentNode = None
        childNode = None

        curNode = nodes.get(self._graph.getEndId())
        curNode.setUpRank(0)
        curNode.setScheduled()
        for parent in curNode.getParents():
            candidateNodes.put(parent.getId())

        while not candidateNodes.empty():
            thisTime = None
            maxTime = None
            maxMIPS = None
            curNode = nodes.get(candidateNodes.get())
            maxTime = -1
            for child in curNode.getChildren():
                childNode = nodes.get(child.getId())
                thisTime = round(childNode.getUpRank() + float(child.getDataSize() / self._bandwidth))
                # print(str(child.getId()) + " " + str(round(child.getDataSize() / self._bandwidth)))
                if thisTime > maxTime:
                    maxTime = thisTime

            maxMIPS = self._resources.getMeanMIPS()
            maxTime += ceil(float(curNode.getInstructionSize() / maxMIPS))

            if curNode.getId() == "start":
                maxTime += 1

            curNode.setUpRank(maxTime)
            curNode.setScheduled()

            for parent in curNode.getParents():
                isCandidate = True
                parentNode = nodes.get(parent.getId())
                for child in parentNode.getChildren():
                    if not nodes.get(child.getId()).isScheduled():
                        isCandidate = False
                if isCandidate:
                    candidateNodes.put(parent.getId())

        for node in nodes.values():
            node.setUnscheduled()

    def getDataSize(self, parent, child):
        size = 0
        for link in parent.getChildren():
            if link.getId() == child.getId():
                size = link.getDataSize()
                break
        return size

    def setEndNodeAST(self):
        endTime = -1
        endNode = self._graph.getNodes().get(self._graph.getEndId())
        for parent in endNode.getParents():
            curEndTime = self._graph.getNodes().get(parent.getId()).getAFT()
            if endTime < curEndTime:
                endTime = curEndTime

        endNode.setAST(int(round(endTime)))
        endNode.setAFT(int(round(endTime)))

        return endNode.getAFT()

    def initializeStartEndNodes(self, startTime, deadline):
        nodes = self._graph.getNodes()

        nodes.get(self._graph.getStartId()).setDeadline(0)
        nodes.get(self._graph.getStartId()).setAFT(0)

        nodes.get(self._graph.getEndId()).setDeadline(deadline)

        nodes.get(self._graph.getStartId()).setScheduled()
        nodes.get(self._graph.getEndId()).setScheduled()

    def solutionAsString(self):  # check this please !!
        headersList = ["N", "R", "EST", "runtime", "EFT", "LST", "LFT", "DeadLine", "cost"]
        rowsList = []
        for node in self._graph.nodes.values():
            tmp = []
            tmp.append(str(node.getId()))
            tmp.append(str(node.getSelectedResource()))
            tmp.append(str(node.getEST()))
            tmp.append(str(node.getRunTime()))
            tmp.append(str(node.getEFT()))
            tmp.append(str(node.getLST()))
            tmp.append(str(node.getLFT()))
            tmp.append(str(node.getDeadline()))
            if node.getSelectedResource() == -1:
                tmp.append("")
            else:
                tmp.append(self._resources.getResource(node.getSelectedResource()).getCost())

            rowsList.append(tmp)

        val2 = [i for i in range(len(rowsList))]
        fig, ax = plt.subplots()
        ax.set_axis_off()
        table = ax.table(
            cellText=rowsList,
            rowLabels=val2,
            colLabels=headersList,
            rowColours=["skyblue"] * len(rowsList),
            colColours=["skyblue"] * 9,
            cellLoc='center',
            loc='center')

        # ax.set_title('WorkflowPolicy.solution',
        # fontweight="bold")

        # plt.rcParams.update({'font.size': 1})

        plt.show()

    def computeFinalCost(self):
        totalCost = 0
        curCost = None

        for instId in range(len(self._instances)):
            inst = self._instances[instId]

            if inst.getFinishTime() == 0:
                break
            first = self._graph.getNodes().get(inst.getFirstTask())
            last = self._graph.getNodes().get(inst.getLastTask())
            curCost = float(ceil(float((last.getEFT() - first.getEST())) / float(
                self._resources.getInterval()))) * inst.getType().getCost()
            totalCost += curCost

        return totalCost

