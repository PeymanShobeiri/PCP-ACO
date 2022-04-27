import sys
sys.path.append('/Users/apple/Desktop/Create WS-ACO/MyCode')
from IaaSCloudWorkflowScheduler.WorkflowPolicy import WorkflowPolicy 
from IaaSCloudWorkflowScheduler.Instance import Instance
from math import ceil

class ICLossPolicy2(WorkflowPolicy):
    def __init__(self, g, rs, bw):
        super().__init__(g, rs, bw)
    
    class result:
            cost = None
            finishTime = None

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
        # difference with PCPD2
        if finishTime != 0 and curStart > curIntervalFinish:
            r.finishTime = sys.maxsize
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
        curNode.setRunTime(curFinish - curStart)
        curNode.setScheduled()

        if curInst.getFinishTime() == 0 :
            curInst.setStartTime(curStart)
            curInst.setFirstTask(curNode.getId())
        
        curInst.setFinishTime(curFinish)
        curInst.setLastTask(curNode.getId())
        curInst.addTask(curNode)

        if curNode.getEFT() > curNode.getLFT():
            return False
        else:
            return True

    def updateParentsLFT(self, childNode):
        for parent in childNode.getParents():
            parentNode = self._graph.getNodes().get(parent.getId())
            newLFT = None
        
            newLFT = childNode.getLST()
            if parentNode.getSelectedResource() != childNode.getSelectedResource():
                newLFT -= round(float(parent.getDataSize()) / self._bandwidth)
            if parentNode.getLFT() > newLFT:
                parentNode.setLFT(newLFT)
                parentNode.setLST(int(newLFT - round(parentNode.getRunTime())))
                self.updateParentsLFT(parentNode)

    def updateChildrenEST(self, curNode):
        start = None
        curStart = None

        for child in curNode.getChildren():
            childNode = self._graph.getNodes().get(child.getId())
            curStart = sys.maxsize

            for parent in childNode.getParents():
                parentNode = self._graph.getNodes().get(parent.getId())
                start = parentNode.getEFT()

                if parentNode.getSelectedResource() != childNode.getSelectedResource():
                    start += round(float(parent.getDataSize()) / self._bandwidth)
                if start > curStart:
                    curStart = start
            
            childNode.setEST(curStart)
            childNode.setEFT(int(curStart + round(childNode.getRunTime())))
            self.updateChildrenEST(childNode)


    def checkCheaperResource(self, inst, newRes):
        success = True
        r = self.result()
        newInst = Instance(self._instances.getSize(), self._resources.getResource(newRes))

        for i in range(len(inst.getTasks())):
            curTask = inst.getTasks()[i]
            if not self.setInstance(curTask, newInst):
                success = False
            self.updateChildrenEST(curTask)
        
        if success:
            r.finishTime = int(newInst.getFinishTime() - newInst.getStartTime())
            r.cost = float(ceil(float(r.finishTime) / float(self._resources.getInterval())) * newInst.getType().getCost())
        else:
            r.finishTime = sys.maxsize
            r.cost = sys.maxsize
        
        inst.setFinishTime(0)
        inst.setStartTime(0)
        inst.getTasks().clear()
        for i in range(len(newInst.getTasks())):
            curTask = newInst.getTasks()[i]
            self.setInstance(curTask, inst)
            self.updateChildrenEST(curTask)
        
        return r

    def setCheaperResource(self, inst, newRes):
        newInst = Instance(self._instances.getSize() , self._resources.getResource(newRes))
        self._instances.addInstance(newInst)

        for i in range(len(inst.getTasks())):
            curTask = inst.getTasks()[i]
            self.setInstance(curTask, newInst)
            self.updateChildrenEST(curTask)
            self.updateParentsLFT(curTask)
        
        inst.setFinishTime(0)
        inst.setStartTime(0)
        inst.getTasks().clear()

    def planning(self):
        queue = self.PriorityQueue()
        r = self.result()

        self.computeUpRank()
        for node in self._graph.nodes.values():
            if not node.getId() == self._graph.getStartId() and not node.getId() == self._graph.getEndId():
                queue.insert(node)
        # initial assignment
        while not queue.isEmpty():
            curNode = queue.remove()
            bestInst = -1
            bestFinish = sys.maxsize

            for curInst in range (self._instances.getSize()):
                r = self.checkInstance(curNode, self._instances.getInstance(curInst))
                if r.finishTime < bestFinish : 
                    bestFinish = r.finishTime
                    bestInst = curInst
            
            # now checking lunching a new instance
            inst = Instance(self._instances.getSize(), self._resources.getResource(0))
            r = self.checkInstance(curNode , inst)
            if r.finishTime < bestFinish:
                bestFinish = r.finishTime
                bestInst = inst.getId()
                self._instances.addInstance(inst)
            
            self.setInstance(curNode, self._instances.getInstance(bestInst))
            self.updateParentsLFT(curNode)
        
        # refining the initial schedule
        contSw = True
        while True:
            minWeight = sys.maxsize
            minInst = -10
            minRes = -10

            for i in range(self._instances.getSize()):
                curInst = self._instances.getInstance(i)
                curCost = None
                weight = sys.maxsize
                curTime = None

                curTime = curInst.getFinishTime() - curInst.getStartTime()
                curCost = float(ceil(float(curTime) / float(self._resources.getInterval())) * curInst.getType().getCost())
                j = curInst.getType().getId() + 1
                while j < self._resources.getSize():
                    r = self.checkCheaperResource(curInst, j)
                    if r.cost < sys.maxsize:
                        if curCost - r.cost > 0 and r.finishTime - curTime > 0:
                            weight = 1 / (curCost - r.cost)
                    else:
                        weight = sys.maxsize
                    if weight < minWeight:
                        minWeight = weight
                        minInst = i
                        minRes = j
                    j += 1
            
            if minWeight < sys.maxsize:
                self.setCheaperResource(self._instances.getInstance(minInst), minRes)
            else:
                contSw = False
            
            if contSw == False:
                break

    
    def removeEmptyInstances(self):
        for i in range(self._instances.getSize()):
            curInst = self._instances.getInstance(i)

            if curInst.getFinishTime() == 0:
                self._instances.removeInstance(curInst)
                i -= 1
    
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
        self.initializeStartEndNodes(startTime, deadline)

        self.planning()
        self.removeEmptyInstances()

        self.setEndNodeEST()
        cost = super().computeFinalCost()
        return cost

