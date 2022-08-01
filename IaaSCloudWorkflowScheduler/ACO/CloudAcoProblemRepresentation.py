import sys

sys.path.append('/Users/apple/Desktop/Create WS-ACO/MyCode')
from IaaSCloudWorkflowScheduler.ACO.CloudAcoProblemNode import CloudAcoProblemNode
from IaaSCloudWorkflowScheduler.ACO.CloudAcoResourceInstanceSet import CloudAcoResourceInstanceSet

from queue import Queue
import warnings

import sys

#
# class AtomicInteger():
#     def __init__(self, value=0):
#         self._value = int(value)
#         self._lock = threading.Lock()
#
#     def inc(self, d=1):
#         with self._lock:
#             self._value += int(d)
#             return self._value
#
#     def dec(self, d=1):
#         return self.inc(-d)
#
#     @property
#     def value(self):
#         with self._lock:
#             return self._value
#
#     @value.setter
#     def value(self, v):
#         with self._lock:
#             self._value = int(v)
#             return self._value


class CloudAcoProblemRepresentation:
    class result:
        cost = None
        finishTime = None

    class PriorityQueue(object):
        def __init__(self, graph):
            self.queue = []
            self.graph = graph

        def __str__(self):
            return ' '.join([str(i) for i in self.queue])

        def isEmpty(self):
            return len(self.queue) == 0

        def insert(self, data):
            self.queue.append(data)

        def computeTotalChild(self, node):
            number = 0
            for child in node.getChildren():
                childNode = self.graph.getNodes().get(child.getId())
                if not childNode.isScheduled():
                    number += self.computeTotalChild(childNode)
                    number += 1
                    childNode.setScheduled()
            return number

        def setAllChildUnscheduled(self, node):
            for child in node.getChildren():
                childNode = self.graph.getNodes().get(child.getId())
                self.setAllChildUnscheduled(childNode)
                childNode.setUnscheduled()

        def compare(self, node1, node2):
            childNumber1 = self.computeTotalChild(node1)
            self.setAllChildUnscheduled(node1)
            childNumber2 = self.computeTotalChild(node2)
            self.setAllChildUnscheduled(node2)
            if childNumber2 > childNumber1:
                return 1
            elif childNumber2 < childNumber1:
                return -1
            else:
                return 0

        def remove(self):  # check for time complexity !!!
            try:
                # maxi = 0
                i = 0
                while i < len(self.queue) - 1:
                    if self.compare(self.queue[i], self.queue[i+1]) == 1:
                        self.queue[i], self.queue[i+1] = self.queue[i+1], self.queue[i]
                    i += 1
                item = self.queue.pop(0)
                # del self.queue[maxi]
                return item
            except IndexError:
                print('Error !!!')
                exit()

    def getGraph(self):
        return self.__graph

    def selectNextTopoNode(self, node, nodesPriorityQueue, workflowNodes):
        for child in node.getChildren():
            childNode = self.__graph.getNodes().get(child.getId())
            isChildValid = True

            for parent in childNode.getParents():
                parentNode = self.__graph.getNodes().get(parent.getId())

                if parentNode not in workflowNodes:
                    isChildValid = False
                    break

            if isChildValid:
                nodesPriorityQueue.insert(childNode)

        return nodesPriorityQueue.remove()

    def topologicalSort(self):
        nodesPriorityQueue = self.PriorityQueue(self.__graph)
        workflowNodes = []
        curNode = self.__graph.getNodes().get("start")
        workflowNodes.append(curNode)

        i = 1
        while i < self.getGraph().getNodeNum():
            curNode = self.selectNextTopoNode(curNode, nodesPriorityQueue, workflowNodes)
            workflowNodes.append(curNode)
            i += 1

        return workflowNodes

    def computeUpRank(self):
        candidateNodes = Queue()
        nodes = self.__graph.getNodes()
        curNode = None
        parentNode = None
        childNode = None

        curNode = nodes.get(self.__graph.getEndId())
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
                thisTime = round(childNode.getUpRank() + float(child.getDataSize() / self.__bandwidth))
                # print(str(child.getId()) + " " + str(round(child.getDataSize() / self.__bandwidth)))
                if thisTime > maxTime:
                    maxTime = thisTime

            maxMIPS = self.__resourceSet.getMeanMIPS()
            maxTime += round(float(curNode.getInstructionSize() / maxMIPS))

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

    warnings.filterwarnings("ignore")

    def createProblemNodeList(self, graph, resourceSet):
        # id = AtomicInteger()
        id = 0
        problemNodeList = []
        numbersOfTasks = graph.getNodeNum()

        nodes = graph.getNodes()
        queue = self.PriorityQueue(graph)
        r = self.result()
        bestFinish = sys.maxsize

        self.computeUpRank()

        for curNode in self.__sortedWorkflowNodes:
            curNode.setUnscheduled()
            for instances in self.__instanceSet.getInstances().values():
                if curNode.getId() == "start":
                    self.__start = CloudAcoProblemNode(curNode, instances[0], id)
                    problemNodeList.append(self.__start)
                elif curNode.getId() == "end":
                    self.__end = CloudAcoProblemNode(curNode, instances[0], id)
                    problemNodeList.append(self.__end)
                else:
                    for instance in instances:
                        node = CloudAcoProblemNode(curNode, instance, id)
                        id += 1
                        problemNodeList.append(node)

        return problemNodeList

    def calculateConstantNeighbours(self):
        neighbours = {}
        for node in self.__graph.nodes.values():
            neighboursList = []

            for cloudAcoProblemNode in self.__problemNodeList:
                if cloudAcoProblemNode.getNode() == node:
                    neighboursList.append(cloudAcoProblemNode)

            neighbours[node] = neighboursList

        return neighbours

    def __init__(self, graph, resourceSet, bandwidth, deadline, instanceCount):
        self.START_NODE_ID = -1
        self.START_NODE_PHEROMONE = 0.0001
        self.__graph = graph
        self.__resourceSet = resourceSet
        self.__instanceSet = CloudAcoResourceInstanceSet(resourceSet, instanceCount)    # create a maxpaller * resource_type instance
        self.__bandwidth = bandwidth
        self.__deadline = deadline
        self.__start = None
        self.__end = None
        self.__sortedWorkflowNodes = self.topologicalSort()         # topology sort of nodes whiich comes first on the table
        self.__problemNodeList = self.createProblemNodeList(self.__graph, self.__instanceSet)
        self.__neighbours = self.calculateConstantNeighbours()
        self.__lacoSortedWorkflowNodes = []

    def resetNodes(self):
        for node in self.__problemNodeList:
            node.resetNode()

    def getNeighbours(self, node):
        return self.__neighbours.get(self.__sortedWorkflowNodes[self.__sortedWorkflowNodes.index(node) + 1])

    def getGraphSize(self):
        return self.__graph.getNodeNum()

    def getStartNode(self):
        return CloudAcoProblemNode()

    def getProblemNodeList(self):
        return self.__problemNodeList

    def getBandwidth(self):
        return self.__bandwidth

    def getInstanceSet(self):
        return self.__instanceSet

    def getDeadline(self):
        return self.__deadline

    def lacoSort(self, sortedTaskIds):
        self.__lacoSortedWorkflowNodes = self.__sortedWorkflowNodes
        # sorted(self.__lacoSortedWorkflowNodes , key = lambda task : sortedTaskIds.index(task.getId()))
        self.__lacoSortedWorkflowNodes.sort(key=lambda task: sortedTaskIds.index(task.getId()))
        self.__sortedWorkflowNodes = self.__lacoSortedWorkflowNodes

    def getStart(self):
        return self.__start

    def getEnd(self):
        return self.__end

    def computeChildes(self, node):
        workflowNodes = []
        for child in node.getChildren():
            childNode = self.__graph.getNodes().get(child.getId())
            workflowNodes.extend(self.computeChildes(childNode))
            workflowNodes.append(childNode)

        return workflowNodes

    def computeParents(self, node):
        workflowNodes = []
        for parent in node.getParents():
            parentNode = self.__graph.getNodes().get(parent.getId())
            workflowNodes.extend(self.computeParents(parentNode))
            workflowNodes.append(parentNode)

        return workflowNodes

    def calculateNeighbours(self):
        neighbours = {}
        for node in self.__graph.nodes.values():
            neighboursList = []
            childes = []
            for child in node.getChildren():
                childNode = self.__graph.getNodes().get(child.getId())
                childes.extend(self.computeChildes(childNode))

            parents = self.computeParents(node)

            for cloudAcoProblemNode in self.__problemNodeList:
                if not cloudAcoProblemNode.getNode() == node and not cloudAcoProblemNode.getNode() in childes and not cloudAcoProblemNode.getNode() in parents:
                    neighboursList.append(cloudAcoProblemNode)

            neighbours[node] = neighboursList

        return neighbours

    def updateChildrenEST(self, parentNode):
        for child in parentNode.getChildren():
            childNode = self.__graph.getNodes().get(child.getId())
            newEST = None

            if not childNode.isScheduled():
                newEST = parentNode.getAFT()
                if childNode.getEST() < newEST:
                    childNode.setEST(newEST)
                    childNode.setEFT(int(newEST + round(childNode.getRunTime())))
                    self.updateChildrenEST(childNode)

    def updateNeighboures(self, cloudAcoProblemNode):  # check for repited
        for nodeListMap in self.__neighbours:
            nodeList = list(nodeListMap.values())
            for i in range(len(nodeList)):
                problemNode = nodeList[i]
                if problemNode.getNode().getId() == cloudAcoProblemNode.getNode().getId():
                    del nodeList[i]
                    i -= 1
