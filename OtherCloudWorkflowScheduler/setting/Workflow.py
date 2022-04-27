from random import random
import sys
from .VM import VM
from matplotlib.collections import Collection
sys.path.append('/Users/apple/Desktop/Create WS-ACO/MyCode')
from IaaSCloudWorkflowScheduler.Constants import Constants
from.Task import Task
from .Edge import Edge
import xml.sax




class Workflow(object):

    def bind(self):
        tentry = self.Array[0]
        texit = self.Array[len(self.Array) - 1]
        for td in self.__transferData.values():
            source  = td.getSource()
            destinations = td.getDestinations()
            if source == None:
                source = tentry
                td.setSize(0)
            
            if destinations == None or len(destinations) == 0:
                destinations.append(texit)
            for destination in destinations:
                flag = True
                for outEdge in source.getOutEdges():
                    if outEdge.getDestination() == destination:
                        outEdge.setDataSize(td.getSize())
                        flag = False
                
                if flag == True:
                    e = Edge(source , destination)
                    e.setDataSize(td.getSize())
                    source.insertOutEdge(e)
                    destination.insertInEdge(e)
                    print("**************add a control flow*******************source: " + e.getSource().getName() + "; destination: " + e.getDestination().getName())
    
    class PriorityQueue(object):
        def __init__(self):
            self.queue = []
  
        def __str__(self):
            return ' '.join([str(i) for i in self.queue])
  
        def isEmpty(self):
            return len(self.queue) == 0
  
        def insert(self, data):
            self.queue.append(data)
        
        def size(self):
            return len(self.queue)

        def remove(self):               # check for time complexity !!!
            try:
                max = 0
                for i in range(len(self.queue)):
                    if (len(self.queue[i].getOutEdges()) - len(self.queue[max].getInEdges())) < (len(self.queue[max].getOutEdges()) - len(self.queue[max].getInEdges())) :
                        max = i
                item = self.queue[max]
                del self.queue[max]
                return item
            except IndexError:
                print('Error !!!')
                exit()

    def topoSort(self):
        topoList = []
        S = self.PriorityQueue()
        S.insert(self.Array[0])

        for task in self.Array:
            task.setTopoCount(0)
        
        self.__maxParallel = -1
        while S.size() > 0:
            self.__maxParallel = max(self.__maxParallel , S.size)
            task = S.remove()
            topoList.append(task)
            for e in task.getOutEdges():
                t = e.getDestination()
                t.setTopoCount(t.getTopoCount() + 1)
                if t.getTopoCount() == len(t.getInEdges()):
                    S.insert(t)
        
        print("An approximate value for maximum parallel number: " + self.__maxParallel)
        ecForDestination = Edge.EComparator(True, topoList)
        ecForSource = Edge.EComparator(False , topoList)
        for t in self.Array:
            sorted(t.getInEdges(), key=ecForSource)
            sorted(t.getOutEdges(), key=ecForDestination)
        
        self.Array = topoList
    

    def calcTaskLevels(self):
        speed = VM.SPEEDS[VM.FASTEST] * Constants.STANDARD_MIPS
        
        j = len(self.Array) - 1
        while j >= 0:
            bLevel = 0.0
            sLevel = 0.0
            task = self.Array[j]
            for outEdge in task.getOutEdges():
                child = outEdge.getDestination()
                bLevel = max(bLevel, child.getbLevel() + outEdge.getDataSize() / VM.NETWORK_SPEED)
                sLevel = max(sLevel, child.getsLevel())
            
            task.setbLevel(bLevel + task.getInstructionSize() / speed)
            task.setsLevel(sLevel + task.getInstructionSize() / speed)
            j -= 1
        
        j = len(self.Array) - 1
        while j >= 0:
            task = self.Array[j]
            ALAP = self.Array[0].getbLevel()
            for outEdge in task.getOutEdges():
                child = outEdge.getDestination()
                ALAP = min(ALAP, child.getALAP() - outEdge.getDataSize() / VM.NETWORK_SPEED)
            
            task.setALAP(ALAP - task.getInstructionSize() / speed)
            j -= 1

        for task in self.Array:
            arrivalTime = 0
            for inEdge in task.getInEdges():
                parent = inEdge.getSource()
                arrivalTime = max(arrivalTime, parent.gettLevel() + parent.getInstructionSize() / speed + inEdge.getDataSize() / VM.NETWORK_SPEED)
            task.settLevel(arrivalTime)
        
        sorted(self.Array , key=Task.BLevelComparator())
        reversed(self.Array)
        print("topological sort and blevel")
        for t in self.Array:
            print(t.getName() + "\t" + t.getbLevel())
        

    


    def __init__(self , file) -> None:
        self.__serialVersionUID =1
        self.__deadline = sys.maxsize
        self.__maxParallel = 0

        self.transferData = {}
        self.nameTaskMapping = {}
        self.Array = []
        Task.resetInternalId()
        try:
            parser = xml.sax.make_parser()
            # parser.setFeature(xml.sax.handler.feature_namespaces , 0)
            Handler = self.createMyDAXReader()
            parser.setContentHandler(Handler)
            parser.parse(file)
            print("succeed to read DAX data from " + file)
        except Exception:
            print("Error in reading a file ")
        
        # -----add tasks to this workflow: start-----
        for t in self.__nameTaskMapping:
            self.Array.append(t)
        tentry = Task("entry", 0)
        texit = Task("exit", 0)
        for t in self.Array:
            if len(t.getInEdges()) == 0:
                e = Edge(tentry, t)
                t.getInEdges().append(e)
                tentry.getOutEdges().append(e)
            
            if len(t.getOutEdges()) == 0:
                e = Edge(t,texit)
                t.getOutEdges().append(e)
                texit.getInEdges().append(e)

        self.Array.insert(0,tentry)
        self.Array.append(texit)

        # ---add tasks to this workflow: end---
        self.bind()
        self.topoSort()
        self.calcTaskLevels()
    
    def calcPURank(self, theta):
        speed = VM.SPEEDS[VM.FASTEST] * Constants.STANDARD_MIPS
        j = len(self.Array) - 1
        while j >= 0:
            pURank = 0.0
            task = self.Array[j]
            for outEdge in task.getOutEdges():
                child = outEdge.getDestination()
                flag = 1
                if theta != sys.maxsize:
                    et = child.getInstructionSize() / speed
                    tt = outEdge.getDataSize() / VM.NETWORK_SPEED
                    d = 1 - pow(theta, -et / tt)
                    if d < random():
                        flag = 0
                
                pURank = max(pURank, child.getpURank() + flag * outEdge.getDataSize() / VM.NETWORK_SPEED)
            
            task.setpURank(pURank + task.getInstructionSize() / speed)
            j -= 1
    
    def getDeadline(self):
        return self.__deadline
    
    def setDeadline(self, deadline):
        self.__deadline = deadline
    
    def getMaxParallel(self):
        return self.__maxParallel
    
    def createMyDAXReader(self):
        return Workflow.MyDAXReader(self)

    
    class MyDAXReader(xml.sax.ContentHandler, object):
        
        def __init__(self, outer):
            self.__outer = outer
            self.__CurrentData = ""
            self.__tags = []
            self.__childId = ""
            self.__lastTask = None
        
        def startElement(self, uri , localName , qName, attrs):
            self.__CurrentData = qName
            if qName == "job":
                id = attrs["id"]
                if id in list(self.__outer.nameTaskMapping.keys()):
                    raise RuntimeError()
                t = Task(id , float(attrs["reuntime"]))
                self.__outer.nameTaskMapping[id] = t
                self.__lastTask = t
            elif qName == "uses" and self.__tags[len(self.__tags) - 1] == "job":
                # After reading the element "job", the element "uses" means a trasferData (i.e., data flow)
                filename = attrs["file"]
                fileSize = int(attrs["size"])
                td = self.__outer.transferData[filename]
                if td == None:
                    td = Workflow.TransferData(filename , fileSize)
                if attrs["link"] == "input" :
                    td.addDestination(self.__lastTask)
                else:
                    td.setSource(self.__lastTask)
                self.__outer.transferData[filename] = td
            elif qName == "child":
                self.__childId = attrs["ref"]
            elif qName == "parent":
                # After reading the element "child", the element "parent" means an edge (i.e., control flow)
                child = self.__outer.nameTaskMapping[self.__childId]
                parent= self.__outer.nameTaskMapping[attrs["ref"]]

                e = Edge(parent , child)
                parent.insertOutEdge(e)
                child.insertInEdge(e)
            
            self.__tags.append(qName)
        
        def endElement(self ,uri, localName, qName):
            tmp = self.__tags.pop()


    


    class TransferData:
        def __init__(self , name , size ):
            self.__name = name
            self.__size = size
            self.__source = None
            self.__destinations = []
        
        def getSize(self):
            return self.__size
        
        def setSize(self , size):
            self.__size = size
        
        def getSource(self):
            return self.__source
        
        def setSource(self, source):
            self.__source = source
        
        def addDestination(self , t):
            self.__destinations.append(t)
        
        def getDestinations(self):
            return self.__destinations
        
        def __str__(self) -> str:
            return "TransferData [name=" + self.__name + ", size=" + self.__size + "]"


                
