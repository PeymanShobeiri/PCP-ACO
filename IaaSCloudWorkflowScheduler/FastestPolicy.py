import sys

sys.path.append('/Users/apple/Desktop/Create WS-ACO/MyCode')
from IaaSCloudWorkflowScheduler.WorkflowPolicy import WorkflowPolicy

from queue import Queue


class FastestPolicy(WorkflowPolicy):
    def __init__(self, g, rs, bw):
        super().__init__(g, rs, bw)

    def schedule(self, startTime, deadline):
        candidateNodes = Queue()
        nodes = self._graph.getNodes()
        curNode = None
        parentNode = None
        childNode = None

        self.setRuntimes()
        curNode = nodes.get(self._graph.getStartId())
        curNode.setAFT(startTime)
        curNode.setScheduled()
        for child in curNode.getChildren():
            candidateNodes.put(child.getId())

        while not candidateNodes.empty():
            thisTime = None
            maxTime = None
            curNode = nodes.get(candidateNodes.get())
            maxTime = -1
            for parent in curNode.getParents():
                parentNode = nodes.get(parent.getId())
                thisTime = parentNode.getAFT()
                if thisTime > maxTime:
                    maxTime = thisTime

            curNode.setAST(maxTime)
            curNode.setAFT(int(maxTime + round(curNode.getRunTime())))
            curNode.setScheduled()
            curNode.setSelectedResource(0)

            for child in curNode.getChildren():
                isCandidate = True
                childNode = nodes.get(child.getId())
                for parent in childNode.getParents():
                    if not nodes.get(parent.getId()).isScheduled():
                        isCandidate = False
                if isCandidate:
                    candidateNodes.put(child.getId())

        totalTime = super().setEndNodeAST()

        #####################  je suis ici
        from math import ceil
        maxCost = self._resources.getMaxCost()
        totalCost = float(ceil(float(totalTime) / float(self._resources.getInterval())) * maxCost)
        return totalCost
        #####################
