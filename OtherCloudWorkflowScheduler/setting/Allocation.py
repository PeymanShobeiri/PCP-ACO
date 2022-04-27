from .VM import VM

class Allocation:

    def __init__(self , vm , task, startTime):
        ######### only for ICPCP ###########
        if type(vm == int):
            self.__vm = None
            self.__task = task
            self.__startTime = startTime
            self.__finishTime = startTime + (task.getInstructionSize() / (VM.SPEEDS[vm]))

        ####################################
        else:
            self.__task = task
            self.__vm = vm
            self.__startTime = startTime
            if vm != None and task != None:
                self.__finishTime = startTime + (task.getInstructionSize() / vm.getMIPS())
        
 

    def getVM(self):
        return self.__vm
    
    def setVM(self , vm):
        self.__vm = vm
    
    def getTask(self):
        return self.__task

    def setTask(self, task):
        self.__task = task
    
    def getStartTime(self):
        return self.__startTime
    
    def setStartTime(self, startTime):
        self.__startTime = startTime
    
    def getFinishTime(self):
        return self.__finishTime
    
    def setFinishTime(self , finishTime):
        self.__finishTime = finishTime
    
    def __str__(self):
        return "Allocation [task=" + self.__task + ", startTime=" + self.__startTime + ", finishTime=" + self.__finishTime + "]"
        