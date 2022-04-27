import sys
sys.path.append('/Users/apple/Desktop/Create WS-ACO/MyCode')
from IaaSCloudWorkflowScheduler.WorkflowPolicy import WorkflowPolicy
from math import ceil


class CheapestPolicy(WorkflowPolicy):
    
    def __init__(self, g, rs, bw):
        super().__init__(g, rs, bw)

    def schedule(self, startTime, deadline):
        minMIPS = self._resources.getMinMIPS()
        minCost = self._resources.getMinCost()
        totalCost = None
        totalTime = 0

        for curNode in self._graph.getNodes().values():
            totalTime += round(float(curNode.getInstructionSize() / minMIPS))
        
        totalCost = float(ceil((float(totalTime) / float(self._resources.getInterval()))) * minCost)
        self._graph.getNodes().get(self._graph.getEndId()).setAST(int(totalTime))
        return totalCost