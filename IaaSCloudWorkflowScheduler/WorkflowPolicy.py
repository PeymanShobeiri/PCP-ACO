import InstanceSet
import sys
from queue import Queue
import WorkflowNode
from math import ceil

class WorkflowPolicy:
    def __init__(self ,g ,rs ,bw):
        self._MB = 1000000
        self._pricePerMB = 0
        self._graph = g
        self._resources = rs
        self._instances = InstanceSet(self._resources)
        self._bandwidth = bw

    # abstract public float schedule(int startTime, int deadline);

    def setRuntimes(self):
        maxMIPS = self._resources.getMaxMIPS()
        for node in self._graph.getNodes().values():
            node.setRunTime(round(node.getInstructionSize() / maxMIPS))

    def computeLSTandLFT(self,deadline):
        candidateNodes = Queue()
        nodes = self._graph.getNodes()
        curNode = None
        parentNode = None
        childNode = None

        curNode = nodes[self._graph.getEndId()]
        curNode.setLFT(deadline)
        curNode.setLST(deadline)
        curNode.setScheduled()
        for parent in curNode.getParents():
            candidateNodes.put(parent.getId())
        
        while not candidateNodes.empty():
            curNode = nodes.get(candidateNodes.get())            # shouldn't be get insted of remove ?? 
            minTime = sys.maxsize
            for child in curNode.getChildren():
                childNode = nodes.get(child.getId())
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
    
    def computeESTandEFT(self, startTime):
        candidateNodes = Queue()
        nodes = self._graph.getNodes()
        curNode = None
        parentNode = None
        childNode = None

        curNode = nodes.get(self._graph.getStartId())
        curNode.setEST(startTime)
        curNode.setEFT(startTime)
        curNode.setScheduled()
        for child in curNode.getChildren():
            candidateNodes.put(child.getId())
        
        while not candidateNodes.empty():       # maxtime and thistime needed to be decleard here ? 
            curNode = nodes.get(candidateNodes.get())
            maxTime = -1
            for parent in curNode.getParents():
                parentNode = nodes.get(parent.getId())
                thisTime = parentNode.getEFT() + round(float(parent.getDataSize()/self._bandwidth))
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
               thisTime = childNode.getUpRank() + round(float(child.getDataSize()/self._bandwidth))
               if thisTime > maxTime:
                   maxTime = thisTime
            
            maxMIPS = self._resources.getMeanMIPS()
            maxTime += round(float(curNode.getInstructionSize()/maxMIPS))
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
            node.setUnscheduled


    def getDataSize(self, parent, child):
        size = 0
        for link in parent.getChildren():
            if link.getId() == child.getId():
                size = link.getDataSize()
                break
        return size
    
    def setEndNodeAST(self):
        endTime = -1
        endNode = WorkflowNode(self._graph.getNodes().get(self._graph.getEndId()))
        for parent in endNode.getParents():
            curEndTime = self._graph.getNodes().get(parent.getId()).getAFT()
            if endTime < curEndTime:
                endTime = curEndTime
        
        endNode.setAST(int(round(endTime)))
        endNode.setAFT(int(round(endTime)))
    
    def initializeStartEndNodes(self, startTime, deadline):     # voard and table !!!
        nodes = self._graph.getNodes()
        nodes.get(self._graph.getStartId()).setScheduled()
        nodes.get(self._graph.getEndId()).setScheduled()
    
    def solutionAsString(self):  # check this please !!
        headersList = ["N", "R", "EST", "runtime", "EFT", "DeadLine", "cost"]
        rowsList = []
        rowsList.append(headersList)
        for node in self._graph.nodes.values():
            rowsList.append([str(node.getId()),str(node.getSelectedResource()),str(node.getEST()),str(node.getRunTime()),str(node.getEFT()),str(node.getDeadline())])
        return rowsList
    
    def computeFinalCost(self):
        totalCost = 0
        curCost = None

        for instId in range(self._instances.getSize()):
            inst = self._instances.getInstance(instId)

            if inst.getFinishTime() == 0:
                break
            first = self._graph.getNodes().get(inst.getFirstTask())
            last = self._graph.getNodes().get(inst.getLastTask())
            curCost = float(ceil(float((last.getEFT() - first.getEST())) / float(self._resources.getInterval()))) * inst.getType().getCost() # check the math here !!!
            totalCost += curCost
        
        return totalCost
    
    ##### UpRankComparator -- ASTComparator -- childComparator -- allChildComparator
