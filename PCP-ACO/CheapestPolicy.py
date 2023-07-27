import sys

from WorkflowPolicy import WorkflowPolicy
from math import ceil


class CheapestPolicy(WorkflowPolicy):

    def __init__(self, g, rs, bw):
        super().__init__(g, rs, bw)

    def schedule(self, startTime, deadline):
        minMIPS = self._resources.getMinMIPS()
        minCost = self._resources.getMinCost()
        totalCost = 0.0
        totalTime = 0

        for curNode in self._graph.getNodes().values():
            totalTime += round(curNode.getInstructionSize() / minMIPS)

        totalCost = ceil(totalTime / self._resources.getInterval()) * minCost
        self._graph.getNodes().get(self._graph.getEndId()).setAST(int(totalTime))
        return totalCost
