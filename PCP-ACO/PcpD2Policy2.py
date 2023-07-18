from ACO.CloudAcoResourceInstanceSet import CloudAcoResourceInstanceSet
from CloudACO import CloudACO
from ypstruct import structure
from WorkflowPolicy import WorkflowPolicy
from Instance import Instance
from WorkflowNode import WorkflowNode
from math import ceil, floor
from prettytable import PrettyTable
import time
import sys


class PcpD2Policy2(WorkflowPolicy):
    def __init__(self, g, rs, bw):
        super().__init__(g, rs, bw)
        self.sortedWorkflowNodes = self.topologicalSort()
        self.problemNodeList = None

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
        last = len(path) - 1
        pathEST = path[0].getEST()
        pathEFT = path[last].getEFT()
        PSD = path[last].getLFT() - pathEST
        i = 0
        while i <= len(path) - 1:
            curNode = path[i]
            subDeadline = pathEST + int(floor(float(curNode.getEFT() - pathEST) / float(pathEFT - pathEST) * PSD))

            curNode.setDeadline(subDeadline)
            curNode.setScheduled()
            i += 1

    def assignParents(self, curNode):
        criticalPath = []

        criticalPath = self.findPartialCriticalPath(curNode)
        if not criticalPath:
            return

        self.assignPath(criticalPath)
        for i in range(len(criticalPath)):
            self.assignParents(criticalPath[i])

        self.assignParents(curNode)

    def distributeDeadline(self):
        # Use PCP for deadline Distribution
        self.assignParents(self._graph.getNodes().get(self._graph.getEndId()))
        self._graph.getNodes().get(self._graph.getEndId()).setDeadline(0)
        for node in self._graph.getNodes().values():
            node.setUnscheduled()

    def topologicalSort(self):
        self.computeUpRank()
        workflowNodes = sorted(self._graph.getNodes().values(), key=lambda item: item.getUpRank(), reverse=True)
        return workflowNodes

    def createProblemNodeList(self):
        problemNodeList = []
        mId = 0

        for instances in self._instances.getInstances():
            # for instance in instances:
            problemNodeList.append(instances)

        for curNode in self.sortedWorkflowNodes:
            if curNode.getId() == "start":
                self._graph.startNode = curNode
                curNode.setMatrixId(0)
                curNode.setSelectedResource(problemNodeList[-1])

            elif curNode.getId() == "end":
                self._graph.endNodeId = curNode
                curNode.setMatrixId(mId)
                curNode.setSelectedResource(problemNodeList[-1])
            else:
                curNode.setMatrixId(mId)
                mId += 1

        return problemNodeList

    def setEndNodeEST(self):
        endTime = -1
        endNode = self._graph.getNodes().get(self._graph.getEndId())

        for parent in endNode.getParents():
            curEndTime = self._graph.getNodes().get(parent.getId()).getEFT()
            if endTime < curEndTime:
                endTime = curEndTime

        endNode.setEST(endTime)
        endNode.setEFT(endTime)

    def saveSolution(self, best):
        myTable = PrettyTable(["N", "I", "AST", "runtime", "AFT", "LFT"])
        for node in best.solution:
            if node is None:
                continue

            myTable.add_row([str(node["id"]), str(node["selectedInstance"]),
                             str(node["AST"]),
                             str(node["runTime"]), str(node["AFT"]),
                             str(node["LFT"])])
        print(myTable)

    def schedule(self, startTime, deadline):
        cost = None

        self.computeESTandEFT(startTime)
        self.computeLSTandLFT(deadline)
        self.initializeStartEndNodes(startTime, deadline)

        # Use PCP for deadline distribution
        self.distributeDeadline()
        self._graph.setMaxParallel(self.FindMaxParallel())

        # Create the first type of each instance with its id
        self._instances = CloudAcoResourceInstanceSet(self._resources, self._graph.getMaxParallel())

        # Create problem node list
        self.problemNodeList = self.createProblemNodeList()

        # Create cloud ACO instance for running the ACO in order to find the best resource for each node
        cloudACO = CloudACO()
        Start_Time = round(time.time())
        best = cloudACO.schedule(self, deadline)
        Finish_Time = round(time.time())
        print(" The total time is : " + str(Finish_Time - Start_Time))

        self.saveSolution(best)

