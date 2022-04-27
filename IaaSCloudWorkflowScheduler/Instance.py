import Resource
import WorkflowNode


class Instance:
    def __init__(self, newId , t, st = 0, ft = 0):
        self.__id = newId
        self.__type = t  # copy constructor 
        self.__startTime = st
        self.__finishTime = ft
        self.__firstTaskId = ''
        self.__lastTaskId = ''
        self.__tasks = []

    def getStartTime(self):
        return self.__startTime
    
    def setStartTime(self, st):
        if st >= 0:
            self.__startTime = st
        
    def getFinishTime(self):
        return self.__finishTime

    def setFinishTime(self, ft):
        if ft >= 0:
            self.__finishTime = ft
    
    def getId(self):
        return self.__id
    
    def getType(self):
        return self.__type
    
    def getFirstTask(self):
        return self.__firstTaskId

    def setFirstTask(self,id):
        self.__firstTaskId = id

    def getLastTask(self):
        return self.__lastTaskId

    def setLastTask(self, id):
        self.__lastTaskId = id
    
    def getTasks(self):
        return self.__tasks
    
    def addTask(self,task):
        self.__tasks.append(task)