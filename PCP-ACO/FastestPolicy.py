import numpy as np
from WorkflowPolicy import WorkflowPolicy
from math import ceil

class FastestPolicy(WorkflowPolicy):
    def __init__(self, g, rs, bw):
        super().__init__(g, rs, bw)

    def topologicalSort(self):
        self.computeUpRank()
        workflowNodes = sorted(self._graph.getNodes().values(), key=lambda item: item.getUpRank(), reverse=True)
        return workflowNodes

    def schedule(self, startTime, deadline, IC_PCP):
        xx = 0
        kk = 0
        self.setRuntimes()
        self.computeUpRank()
        nodes = self._graph.getNodes()
        sortedWorkflowNodes = self.topologicalSort()
        sortedWorkflowNodes[0].AFT = 0
        ID = 0

        for node in sortedWorkflowNodes:

            if node.id == "start" or node.id == "end":
                continue

            maxTime = -1
            for parent in node.getParents():
                parentNode = nodes.get(parent.getId())
                thisTime = parentNode.AFT + round(parent.dataSize / self._bandwidth)
                if thisTime > maxTime:
                    maxTime = thisTime

            node.setAST(maxTime)
            selected = -1
            minAFT = np.inf
            AST = 0
            sw = 1
            for instance in self._instances:
                cur_start = max(instance["instanceFinishTime"], node.AST)
                curAFT = int(cur_start + ceil(node.instructionSize / instance["resource"].MIPS))
                if curAFT < minAFT:
                    selected = instance["instanceId"]
                    minAFT = curAFT
                    AST = cur_start

            if int(maxTime + ceil(node.instructionSize / self._resources.resources[0].MIPS)) < minAFT:
                sw = 0
                kk += 1
                tmp = {"instanceId": ID, "resource": self._resources.resources[0], "finishDuration": 0,
                       "processedTasksIds": set(), "currentStartTime": 0, "instanceFinishTime": 0.0}
                self._instances.append(tmp)
                node.AST = maxTime
                node.AFT = int(node.AST + ceil(node.instructionSize / tmp["resource"].MIPS))
                selected = ID
                ID += 1

            if sw == 1:
                node.AFT = minAFT
                node.AST = AST

            self._instances[selected]["currentStartTime"] = node.AST
            self._instances[selected]["instanceFinishTime"] = node.AFT
            self._instances[selected]["processedTasksIds"].add(node.id)
            xx += round(node.instructionSize / self._instances[selected]["resource"].MIPS)

        self._graph.nodes[self._graph.getEndId()].AST = sortedWorkflowNodes[-2].AFT
        # print("heft schedualing : " + str(xx/ 3600))
        return 'None'
