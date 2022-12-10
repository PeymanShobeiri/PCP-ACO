import sys
import WorkflowPolicy
from math import ceil
import Instance

class ListPolicy(WorkflowPolicy):
    def __init__(self, g, rs, bw):
        super().__init__(g, rs, bw)

    class result:
            cost = None
            finishTime = None

    def checkInstance(self, curNode, curInst):
        finishTime = curInst.getFinishTime()
        startTime = curInst.getStartTime()
        interval = self._resources.getInterval()
        curCost = ceil(float(finishTime - startTime) / float(interval)) * curInst.getType().getCost()
        curIntervalFinish = startTime + int(ceil(float(finishTime - startTime) / float(interval)) * interval)
        start = None
        curStart = int(finishTime)
        curFinish = None

        for parent in curNode.getParents():
            parentNode = self._graph.getNodes().get(parent.getId())

            start = parentNode.getEFT()
            if parentNode.getSelectedResource() != curInst.getId():
                start += round(float(parent.getDataSize()) / self._bandwidth)
            if start > curStart:
                curStart = start
        
        if finishTime == 0 :
            startTime = curStart
        
        r = self.result()
        curFinish = curStart + round(float(curNode.getInstructionSize()) / curInst.getType().getMIPS())
        r.finishTime = curFinish
        if (finishTime != 0 and curStart > curIntervalFinish) or curFinish > curNode.getLFT():
            r.cost = sys.maxsize
        else: 
            r.cost = float(ceil(float(curFinish - startTime) / float(interval)) * curInst.getType().getCost() - curCost)
        return r

    def setInstance(self, curNode, curInst):
        start = None
        curStart = int(curInst.getFinishTime())
        curFinish = None

        for parent in curNode.getParents():
            parentNode = self._graph.getNodes().get(parent.getId())

            start = parentNode.getEFT()
            if parentNode.getSelectedResource() != curInst.getId():
                start += round(float(parent.getDataSize()) / self._bandwidth)
            if start > curStart:
                curStart = start
        
        curFinish = curStart + round(float(curNode.getInstructionSize()) / curInst.getType().getMIPS())
        curNode.setEST(curStart)
        curNode.setEFT(curFinish)
        curNode.setSelectedResource(curInst.getId())
        curNode.setScheduled()

        if curInst.getFinishTime() == 0:
            curInst.setStartTime(curStart)
            curInst.setFirstTask(curNode.getId())
        
        curInst.setFinishTime(curFinish)
        curInst.setLastTask(curNode.getId())




    def planning(self):
        queue = self.PriorityQueue()
        r = self.result()
        bestFinish = sys.maxsize

        self.computeUpRank()
        for node in self._graph.nodes.values():
            if not node.getId() == self._graph.getStartId() and not node.getId() == self._graph.getEndId():
                queue.insert(node)
        
        while not queue.isEmpty():
            curNode = queue.remove()
            bestInst = -1
            bestCost = sys.maxsize

            for curInst in range(self._instances.getSize()):
                r = self.checkInstance(curNode, self._instances.getInstance(curInst))
                if r.cost < bestCost:
                    bestCost = r.cost
                    bestFinish = r.finishTime
                    bestInst = curInst
                elif bestCost < sys.maxsize and r.cost == bestCost and r.finishTime < bestFinish:
                    bestFinish = r.finishTime
                    bestInst = curInst
            
            if bestInst == -1:
                curRes = self._resources.getSize() - 1
                # because the cheapest one is the last
                while curRes >= 0:
                    inst = Instance(self._instances.getSize(), self._resources.getResource(curRes))
                    r = self.checkInstance(curNode, inst)
                    if r.cost < sys.maxsize:
                        bestInst = inst.getId()
                        self._instances.addInstance(inst)
                        break 
                    curRes -= 1

            self.setInstance(curNode, self._instances.getInstance(bestInst))

    def setEndNodeEST(self):
        endTime = -1
        endNode = self._graph.getNodes().get(self._graph.getEndId())

        for parent in endNode.getParents():
            curEndTime = self._graph.getNodes().get(parent.getId()).getEFT()
            if endTime < curEndTime:
                endTime = curEndTime
        
        endNode.setEST(endTime)
        endNode.setEFT(endTime)



    def schedule(self, startTime, deadline):
        cost = None

        self.setRuntimes()
        self.computeESTandEFT(startTime)
        self.computeLSTandLFT(deadline)
        self.initializeStartEndNodes(startTime , deadline)

        self.planning()

        self.setEndNodeEST()
        cost = super().computeFinalCost()
        return cost
    
    
    class PriorityQueue(object):
        def __init__(self):
            self.queue = []
  
        def __str__(self):
            return ' '.join([str(i) for i in self.queue])
  
        def isEmpty(self):
            return len(self.queue) == 0
  
        def insert(self, data):
            self.queue.append(data)
            
  
        def remove(self):               # check for time complexity !!!
            try:
                max = 0
                for i in range(len(self.queue)):
                    if self.queue[i].getUpRank() > self.queue[max].getUpRank():
                        max = i
                item = self.queue[max]
                del self.queue[max]
                return item
            except IndexError:
                print('Error !!!')
                exit()
