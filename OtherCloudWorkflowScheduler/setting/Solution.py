from math import ceil
from .VM import VM
from .Allocation import Allocation
from collections import defaultdict


class Solution:
    def __init__(self) :
        self.__serialVersionUID = 1
        self.__revMapping = {}
        self.__sortedTask = []
        self.hashmap = defaultdict(list)
        VM.resetInternalId()
    
    def getSortedTask(self):
        return self.__sortedTask
    
    def addTaskToVM(self, vm , task , startTime, isEnd):
        self.__sortedTask.append(task)
        if vm in self.hashmap == False:
            self.hashmap[vm] = []

        alloc =  Allocation(vm, task, startTime)
        conflict = False
        startTime1 = alloc.getStartTime()
        finishTime1 = alloc.getFinishTime()
        for prevAlloc in self.hashmap[vm]:
            startTime2 = prevAlloc.getStartTime()
            finishTime2 = prevAlloc.getFinishTime()
            if (startTime1 > startTime2 and startTime2 > finishTime1) or (startTime2 > startTime1 and startTime1 > finishTime2):
                conflict = True
        
        if conflict:
            raise RuntimeError("Critical Error: Allocation conflicts")
        
        if isEnd:
            self.hashmap[vm].append(alloc)
        else:
            self.hashmap[vm].insert(0,alloc)
        self.__revMapping[alloc.getTask()] = alloc

    def updateVM(self, vm):
        vm.setType(vm.getType() + 1)
        list = self.hashmap[vm]
        if list == None:
            return
        for alloc in list:
            newFinishTime = alloc.getTask().getInstructionSize() / vm.getMIPS() + alloc.getStartTime()
            alloc.setFinishTime(newFinishTime)
    
    def getVMReadyTime(self, vm):
        if self.hashmap[vm] == None or len(self.hashmap[vm]) == 0:
            return VM.LAUNCH_TIME
        else:
            allocations = self.hashmap[vm]
            return allocations[len(allocations) -1 ].getFinishTime()
    

    def calcEST(self, task, vm):
        EST = 0.0
        for inEdge in task.getInEdges():
            parent = inEdge.getSource()
            alloc = self.__revMapping[parent]
            parentVM = alloc.getVM()
            arrivalTime = alloc.getFinishTime()
            if parentVM != vm:
                arrivalTime += inEdge.getDataSize() / VM.NETWORK_SPEED
            EST = max(EST , arrivalTime)
        
        if vm == None:
            EST = max(EST,VM.LAUNCH_TIME)
        else:
            EST = max(EST, self.getVMReadyTime(vm))
        return EST
    
    def getVMLeaseEndTime(self, vm):
        if self.hashmap[vm] == None or len(self.hashmap[vm]) ==0:
            return VM.LAUNCH_TIME
        else:
            allocations = self.hashmap[vm]
            lastTask = allocations[len(allocations) - 1].getFinishTime()

            maxTransferTime = 0
            for e in lastTask.getOutEdges():
                alloc = self.__revMapping[e.getDestination()]
                if alloc == None or alloc.getVM() != vm:
                    maxTransferTime = max(maxTransferTime , e.getDataSize() / VM.NETWORK_SPEED)
    
    def getVMLeaseStartTime(self, vm):
        if len(self.hashmap[vm]) == 0:
            return VM.LAUNCH_TIME
        else:
            firstTask = self.hashmap[vm][0].getTask()
            ftStartTime = self.hashmap[vm][0].getStartTime()

            maxTransferTime = 0
            for e in firstTask.getInEdges():
                alloc = self.__revMapping[e.getSource()]
                if alloc == None or alloc.getVM() != vm:
                    maxTransferTime = max(maxTransferTime , e.getDataSize() / VM.NETWORK_SPEED)
            
            return ftStartTime - maxTransferTime
    
    
    def calcVMCost(self, vm):
        a = vm.getUnitCost()
        b = self.getVMLeaseEndTime(vm)
        c = self.getVMLeaseStartTime(vm)
        h = vm.getUnitCost() * ceil((self.getVMLeaseEndTime(vm) - self.getVMLeaseStartTime(vm)) / VM.INTERVAL)
        return vm.getUnitCost() * ceil((self.getVMLeaseEndTime(vm) - self.getVMLeaseStartTime(vm)) / VM.INTERVAL)

    def calcCost(self):
        totalCost = 0.0
        for vm in self.hashmap.keys():
            vmCost = self.calcVMCost(vm)
            totalCost += vmCost
        
        return totalCost
    
    def calcMakespan(self):
        makespan = -1
        for vm in self.hashmap.keys():
            finishTime = self.getVMReadyTime(vm)
            if (finishTime > makespan):
                makespan = finishTime
            
        return makespan
    
    def isBetterThan(self, s, epsilonDeadline) -> bool:
        makespan1 = self.calcMakespan()
        makespan2 = s.calcMakespan()
        cost1 = self.calcCost()
        cost2 = s.calcCost()

        if makespan1 <= epsilonDeadline and makespan2 <= epsilonDeadline:
            return cost1 < cost2
        elif makespan1 > epsilonDeadline and makespan2 > epsilonDeadline:
            return makespan1 < makespan2
        elif makespan1 <= epsilonDeadline and makespan2 > epsilonDeadline:
            return True
        else:
            return not(makespan1 > epsilonDeadline) or not(makespan2 <= epsilonDeadline)
    
    def validate(self , wf):
        list = list(self.__revMapping.values())
        set = {}
        for alloc in list:
            task = alloc.getTask()
            for e in task.getOutEdges():
                child = e.getDestination()

                childAlloc = self.__revMapping[child]
                isValid = False
                if alloc.getVM() != childAlloc.getVM() and alloc.getFinishTime() + e.getDataSize() / VM.NETWORK_SPEED <= childAlloc.getStartTime() + Evaluate.E:
                    isValid = True
                
                elif alloc.getVM() == childAlloc.getVM() and alloc.getFinishTime() <= childAlloc.getStartTime() + Evaluate.E:
                    isValid = True
                if not isValid:
                    return False
        
        return True
    
    def getRevMapping(self):
        return self.__revMapping
    
    def __str__(self) -> str:
        sb = ''
        sb += "required cost: {}\trequired time:\r\n".format(self.calcCost(), self.calcMakespan())
        for vm in self.hashmap.keys():
            sb += "{} {} \r\n".format(vm, self.hashmap[vm])
        
        return sb 
    
