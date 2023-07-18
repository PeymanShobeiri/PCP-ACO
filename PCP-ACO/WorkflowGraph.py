import sys
import DAG
from WorkflowNode import WorkflowNode
from Constants import Constants
from DAG.LinkageType import LinkageType


class WorkflowGraph:
    def __init__(self):
        self.startNode = "start"
        self.endNodeId = "end"
        # self.__jobNumPE = 1
        self.nodes = {}
        self.nodeNum = 0
        self.maxParallel = 0

    def __computeIOsize(self, dag, parentId, childId):
        size = 0
        for parentJob in dag.getJobList():
            if parentJob.getId() == parentId:
                for childJob in dag.getJobList():
                    if childJob.getId() == childId:
                        for outFile in parentJob.getUseList():
                            if outFile.getLink() == "output":
                                for inFile in childJob.getUseList():
                                    if inFile.getLink() == "input" and inFile.getFile() == outFile.getFile():
                                        curSize = int(inFile.getSize())
                                        if curSize > 0:
                                            size += curSize
        return size

    class counter(object):
        def __init__(self, instSize=None):
            if instSize is None:
                self.__maxInstSize = -1
                self.__meanInstSize = 0
                self.__no = 0
            else:
                self.__maxInstSize = instSize
                self.__meanInstSize = instSize
                self.__no = 1

        def add(self, instSize):
            self.__meanInstSize += instSize
            if instSize > self.__maxInstSize:
                self.__maxInstSize = instSize
            self.__no += 1

        def computeMean(self):
            self.__meanInstSize /= self.__no
            return int(self.__meanInstSize)

        def getMean(self):
            return int(self.__meanInstSize)

        def getMax(self):
            return self.__maxInstSize

    def unifyRunTimes(self):
        jobTypes = {}
        for node in self.nodes.values():
            curJob = node.getName()
            if curJob in jobTypes.keys():
                jobTypes.get(curJob).add(node.getInstructionSize())
            else:
                c = self.counter(node.getInstructionSize())
                jobTypes[curJob] = c

        for c in jobTypes.values():
            c.computeMean()

        for node in self.nodes.values():
            curJob = node.getName()
            node.setInstructionSize(jobTypes.get(curJob).getMean())

    def convertDagToWorkflowGraph(self, dag):
        inputFilesSize = None
        outputFilesSize = None
        IOsize = None
        runTime = None

        self.nodes.clear()
        if dag is None:
            return False
        for job in dag.getJobList():
            inputFilesSize = outputFilesSize = 0
            for file in job.getUseList():
                if file.getLink() == "input" and int(file.getSize()) > 0:
                    inputFilesSize += int(file.getSize())
                elif file.getLink() == "output" and int(file.getSize()) > 0:
                    outputFilesSize += int(file.getSize())

            runTime = round(float(job.getRuntime()))
            if runTime <= 0:
                runTime = 1
            wfNode = WorkflowNode(job.getId(), job.getName(), inputFilesSize, outputFilesSize, runTime)
            wfNode.setInstructionSize(runTime * Constants().STANDARD_MIPS)
            # wfNode.setNumPE(self.__jobNumPE)
            self.nodes[job.getId()] = wfNode

        for child in dag.getChildList():
            childId = child.getRef()
            if childId not in self.nodes.keys():
                print("id= " + childId + " doesn't exist!")
                return False
            for parent in child.getParentList():
                IOsize = self.__computeIOsize(dag, parent.getRef(), childId)
                self.nodes[childId].addParent(parent.getRef(), IOsize)  # you can make it two part if didn't work
                self.nodes.get(parent.getRef()).addChild(childId, IOsize)  # same thing here

        startNode = WorkflowNode(self.startNode, self.startNode, 0, 0, 0)
        endNode = WorkflowNode(self.endNodeId, self.endNodeId, 0, 0, 0)
        startNode.setInstructionSize(0)
        endNode.setInstructionSize(0)
        startNode.setNumPE(0)
        endNode.setNumPE(0)
        for node in self.nodes.values():
            if not node.hasParent():
                startNode.addChild(node.getId(), 0)
                node.addParent(startNode.getId(), 0)
            if not node.hasChild():
                node.addChild(endNode.getId(), 0)
                endNode.addParent(node.getId(), 0)

        self.nodes[self.startNode] = startNode
        self.nodes[self.endNodeId] = endNode
        self.nodeNum = len(self.nodes)

        self.unifyRunTimes()

        return True

    def getMaxParallel(self):
        return self.maxParallel

    def setMaxParallel(self, maxParallel):
        self.maxParallel = maxParallel

    def getNodes(self):
        return self.nodes

    def setNodes(self, newNodes):
        self.nodes = newNodes

    def getStartId(self):
        return self.startNode

    def getEndId(self):
        return self.endNodeId

    def getNodeNum(self):
        return self.nodeNum
