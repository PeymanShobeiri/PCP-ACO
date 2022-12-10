import sys
import WorkflowPolicy
from math import ceil
import Instance
import InstanceSet

class ICLossPolicy(WorkflowPolicy):
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
    
    def updateChildrenEST(self, parentNode):
        for child in parentNode.getChildren():
            childNode = self._graph.getNodes().get(child.getId())
            newEST = None

            newEST = parentNode.getEFT()
            if parentNode.getSelectedResource() != childNode.getSelectedResource():
                newEST += round(float(child.getDataSize()) / self._bandwidth)
            if childNode.getEST() < newEST:
                childNode.setEST(newEST)
                childNode.setEFT(int(newEST + round(childNode.getRunTime())))

                self.updateChildrenEST(childNode)
    


    def removeNodeFromInstance(self, node):
        inst = self._instances.getInstance(node.getSelectedResource())

        if inst.getFirstTask() == node.getId():
            if inst.getLastTask() == node.getId():
                inst.setStartTime(0)
                inst.setFinishTime(0)
                inst.setFirstTask("")
                inst.setLastTask("")
            else:
                inst.setFirstTask(inst.getTasks()[1].getId())
                inst.setStartTime(inst.getTasks()[1].getEST())
        else:
            place = inst.getTasks().indexOf(node)
            if inst.getLastTask() == node.getId():
                inst.setFinishTime(inst.getTasks()[place - 1].getEFT())         # Error ? --> use []
                inst.setLastTask(inst.getTasks()[place - 1].getId())
                inst.getTasks().remove(place)
            else:
                firstInterval = (inst.getTasks()[place - 1].getEFT() - inst.getStartTime()) / self._resources.getInterval()
                secondInterval = (inst.getTasks()[place + 1].getEST() - inst.getStartTime()) / self._resources.getInterval()
                if firstInterval != secondInterval:
                    inst.setFinishTime(inst.getTasks()[place - 1].getEFT())
                    inst.setLastTask(inst.getTasks()[place - 1].getId())

                    newInst = Instance(self._instances.getSize(), inst.getType())
                    self._instances.addInstance(newInst)
                    i = place + 1
                    while i > inst.getTasks().size():
                        self.setInstance(inst.getTasks()[i], newInst)
                        self.updateChildrenEST(inst.getTasks()[i])
                        self.updateParentsLFT(inst.getTasks()[i])
                        inst.getTasks().remove(i)
                        i += 1
                
                inst.getTasks().remove(place)


    def checkInstanceWithLFT(self, curNode, curInst):
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
        
        if finishTime == 0:
            startTime = curStart
        
        r = self.result()
        curFinish = curStart + round(float(curNode.getInstructionSize()) / curInst.getType().getMIPS())
        r.finishTime = curFinish
        if (finishTime != 0 and curStart > curIntervalFinish) or curFinish > curNode.getLFT():
            r.cost = sys.maxsize
            r.finishTime = sys.maxsize
        else:
            r.cost = float(ceil(float(curFinish - startTime) / float(interval)) * curInst.getType().getCost() - curCost)
        
        return r

    def rescheduleNode(self, node, newStart):
        inst = self._instances.getInstance(node.getSelectedResource())
        prevInterval = (node.getEST() - inst.getStartTime()) / self._resources.getInterval()
        newInterval = (newStart - inst.getStartTime()) / self._resources.getInterval()
        newFinish = None
        bestFinish = sys.maxsize
        bestInst = 0
        r = self.result()

        if prevInterval == newInterval:
            node.setEST(newStart)
            newFinish = newStart + round(float(node.getInstructionSize()) / inst.getType().getMIPS())
            node.setEFT(newFinish)
            if inst.getLastTask() == node.getId():
                inst.setFinishTime(newFinish)
            if inst.getFirstTask() == node.getId():
                inst.setStartTime(newStart)
        else:
            self.removeNodeFromInstance(node)

            for i in range(self._instances.getSize()):
                curInst = self._instances.getInstance(i)
                if curInst.getType().getId() == inst.getType().getId():
                    r = self.checkInstanceWithLFT(node, curInst)
                    if r.finishTime < bestFinish:
                        bestFinish = r.finishTime
                        bestInst = i
            
            # now checking lunching a new instance
            newInst = Instance(self._instances.getSize(), inst.getType())
            r = self.checkInstanceWithLFT(node, inst)
            if r.finishTime < bestFinish:
                bestFinish = r.finishTime
                bestInst = newInst.getId()
                self._instances.addInstance(newInst)
            self.setInstance(node, self._instances.getInstance(bestInst))
    
            


    def rescheduleChildren(self, curNode):
        start = None

        for child in curNode.getChildren():
            childNode = self._graph.getNodes().get(child.getId())

            start = curNode.getEFT()
            if curNode.getSelectedResource() != childNode.getSelectedResource():
                start += round(float(child.getDataSize()) / self._bandwidth)
            if start > childNode.getEST():
                self.rescheduleNode(childNode, start)
                self.rescheduleChildren(childNode)
                self.updateParentsLFT(childNode)
    


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
            
            self.setInstance(curNode , self._instances.getInstance(bestInst))
            self.updateParentsLFT(curNode)
        
        # first making empty instances
        emptyInstances = InstanceSet(self._resources)
        for curRes in range (self._resources.getSize()):
            inst = Instance(emptyInstances.getSize(), self._resources.getResource(curRes))
            emptyInstances.addInstance(inst)
        
        # refining the initial schedule
        contSw = True
        while True:
            minWeight = sys.maxsize
            minNode = None
            minInst = -10
            minRes = -10

            for curNode in self._graph.nodes.values():
                curCost = None
                weight = None
                curTime = None
                estInterval = None
                eftInterval = None
                instStartTime = None

                if curNode.getId() == self._graph.getStartId() or curNode.getId() == self._graph.getEndId():
                    break
                curTime = curNode.getEFT() - curNode.getEST()
                curCost = float(curTime) / float(self._resources.getInterval() * self._instances.getInstance(curNode.getSelectedResource()).getType().getCost())
                instStartTime = self._instances.getInstance(curNode.getSelectedResource()).getStartTime()

                # first checking cur instances
                for curInst in range(self._instances.getSize()):
                    r = self.checkInstanceWithLFT(curNode, self._instances.getInstance(curInst))
                    if r.cost < sys.maxsize:
                        r.finishTime -= curNode.getEST()
                        r.cost = float(r.finishTime) / float(self._resources.getInterval()) * self._instances.getInstance(curInst).getType().getCost()
                        
                        if curCost - r.cost > 0 and (r.finishTime - curTime) > 0:
                            weight = 1 / (curCost - r.cost)
                        else:
                            weight = sys.maxsize
                        if weight < minWeight:
                            minWeight = weight
                            minNode = curNode
                            minInst = curInst
                
                # now checking for launching a new instance
                for curInst in range(emptyInstances.getSize()):
                    r = self.checkInstanceWithLFT(curNode, emptyInstances.getInstance(curInst))
                    if r.cost < sys.maxsize:

                        r.finishTime -= curNode.getEST()
                        r.cost = float(r.finishTime) / float(self._resources.getInterval()) * emptyInstances.getInstance(curInst).getType().getCost()

                        if curCost - r.cost > 0 and r.finishTime - curTime > 0 :
                            weight = 1 / (curCost - r.cost)
                        else:
                            weight = sys.maxsize
                        if weight < minWeight:
                            minWeight = weight
                            minNode = curNode
                            minInst = -1
                            minRes = curInst
            # end for workflow node
            if minWeight < sys.maxsize:
                self.removeNodeFromInstance(minNode)

                if minInst == -1:
                    inst = Instance(self._instances.getSize(), self._resources.getResource(minRes))
                    self._instances.addInstance(inst)
                    self.setInstance(minNode, inst)
                else:
                    self.setInstance(minNode, self._instances.getInstance(minInst))
                self.updateParentsLFT(minNode)
                self.rescheduleChildren(minNode)
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