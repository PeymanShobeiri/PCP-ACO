from random import random
import sys
from VM import VM
from lxml import etree, objectify
from copy import deepcopy
from matplotlib.collections import Collection
from queue import Queue
sys.path.append('/Users/apple/Desktop/Create WS-ACO/MyCode')
from IaaSCloudWorkflowScheduler.Constants import Constants
from Task import Task
from Edge import Edge
import xml.sax


class Workflow(object):

    # def unifyRunTimes(self):
    #     jobTypes = {}
    #     for node in self.nodes.values():
    #         curJob = node.getName()
    #         if curJob in jobTypes.keys():
    #             jobTypes.get(curJob).add(node.getInstructionSize())
    #         else:
    #             c = self.counter(node.getInstructionSize())
    #             jobTypes[curJob] = c
    #
    #     for c in jobTypes.values():
    #         c.computeMean()
    #
    #     for node in self.nodes.values():
    #         curJob = node.getName()
    #         node.setInstructionSize(jobTypes.get(curJob).getMean())

    def bind(self):
        tentry = self.array[0]
        texit = self.array[len(self.array) - 1]
        for td in self.transferData.values():
            source = td.getSource()
            destinations = td.getDestinations()
            if source is None:
                source = tentry
                td.setSize(0)

            if destinations is None or len(destinations) == 0:
                destinations.append(texit)
            for destination in destinations:
                flag = True
                for outEdge in source.getOutEdges():
                    if outEdge.getDestination() == destination:
                        outEdge.setDataSize(td.getSize())
                        flag = False

                if flag:
                    e = Edge(source, destination)
                    e.setDataSize(td.getSize())
                    source.insertOutEdge(e)
                    destination.insertInEdge(e)
                    print(
                        "**************add a control flow*******************source: " + e.getSource().getName() + "; destination: " + e.getDestination().getName())

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

        def remove(self):  # check for time complexity !!!
            try:
                max = 0
                for i in range(len(self.queue)):
                    if (len(self.queue[i].getOutEdges()) - len(self.queue[max].getInEdges())) < (
                            len(self.queue[max].getOutEdges()) - len(self.queue[max].getInEdges())):
                        max = i
                item = self.queue[max]
                del self.queue[max]
                return item
            except IndexError:
                print('Error !!!')
                exit()

    # kahn algorithm besides, calculate the maximum parallel numberand sort edages for each task
    def topoSort(self):
        topoList = []
        # in real S should be queue but we use list insted
        S = []
        S.append(self.array[0])

        # set topocount to 0
        for task in self.array:
            task.setTopoCount(0)

        self.maxParallel = -1
        while len(S) > 0:
            self.maxParallel = max(self.maxParallel, len(S))
            task = S.pop()
            topoList.append(task)
            for e in task.getOutEdges():
                t = e.getDestination()
                t.setTopoCount(t.getTopoCount() + 1)
                if t.getTopoCount() == len(t.getInEdges()):
                    S.insert(0, t)

        print("An approximate value for maximum parallel number: " + str(self.maxParallel))
        ecForDestination = Edge.EComparator(True, topoList)
        ecForSource = Edge.EComparator(False, topoList)
        # for t in self.array:
        #     sorted(t.getInEdges(), key=lambda x: x.getDestination())
        #     sorted(t.getOutEdges(), key=lambda y: y.getSource())

        self.array = topoList

    def calcTaskLevels(self):
        speed = VM.SPEEDS[VM.FASTEST] * Constants.STANDARD_MIPS

        j = len(self.array) - 1
        while j >= 0:
            bLevel = 0.0
            sLevel = 0.0
            task = self.array[j]
            for outEdge in task.getOutEdges():
                child = outEdge.getDestination()
                bLevel = max(bLevel, child.getbLevel() + outEdge.getDataSize() / VM.NETWORK_SPEED)
                sLevel = max(sLevel, child.getsLevel())

            task.setbLevel(bLevel + task.getInstructionSize() / speed)
            task.setsLevel(sLevel + task.getInstructionSize() / speed)
            j -= 1

        j = len(self.array) - 1
        while j >= 0:
            task = self.array[j]
            ALAP = self.array[0].getbLevel()
            for outEdge in task.getOutEdges():
                child = outEdge.getDestination()
                ALAP = min(ALAP, child.getALAP() - outEdge.getDataSize() / VM.NETWORK_SPEED)

            task.setALAP(ALAP - task.getInstructionSize() / speed)
            j -= 1

        for task in self.array:
            arrivalTime = 0
            for inEdge in task.getInEdges():
                parent = inEdge.getSource()
                arrivalTime = max(arrivalTime,
                                  parent.gettLevel() + parent.getInstructionSize() / speed + inEdge.getDataSize() / VM.NETWORK_SPEED)
            task.settLevel(arrivalTime)

        sorted(self.Array, key=Task.BLevelComparator())
        reversed(self.Array)
        print("topological sort and blevel")
        for t in self.array:
            print(t.getName() + "\t" + t.getbLevel())

    def __init__(self, file):
        self.array = []
        self.nameTaskMapping = {}
        self.lasttask = None
        self.transferData = {}
        self.maxParallel = 0
        self.deadline = 0

        with open(file, 'rb') as f:
            try:
                xxml = f.read()
            except FileNotFoundError:
                print("File not founded")

        root = objectify.fromstring(xxml)
        for i in range(int(root.attrib['jobCount'])):
            idd = root.job[i].attrib['id']
            run = root.job[i].attrib['runtime']
            t = Task(idd, run)
            self.nameTaskMapping[idd] = t
            self.lasttask = t
            for use in root.job[i].uses:
                filename = use.attrib['file']
                filesize = use.attrib['size']
                td = self.transferData.get(filename)
                if td is None:
                    td = self.TransferData(filename, filesize)
                if use.attrib['link'] == "input":
                    td.addDestination(self.lasttask)
                else:
                    td.setSource(self.lasttask)
                self.transferData[filename] = td

        for ch in root.child:
            childid = ch.attrib['ref']
            for p in ch.parent:
                parentid = p.attrib['ref']
                child = self.nameTaskMapping.get(childid)
                parent = self.nameTaskMapping.get(parentid)

                e = Edge(parent, child)
                # ppp = type(parent)
                parent.insertOutEdge(e)
                child.insertInEdge(e)

        tentry = Task("entry", 0)
        texit = Task("exit", 0)

        for t in self.nameTaskMapping.values():
            # xx = type( t)
            if len(t.getInEdges()) == 0:
                e = Edge(tentry, t)
                t.getInEdges().append(e)
                tentry.getOutEdges().append(e)

            if len(t.getOutEdges()) == 0:
                e = Edge(t, texit)
                t.getOutEdges().append(e)
                texit.getInEdges().append(e)

        self.array = list(self.nameTaskMapping.values())
        self.array.insert(0, tentry)
        self.array.append(texit)

        # ---add tasks to this workflow: end---
        # self.unifyRunTimes()
        # self.bind()
        self.topoSort()
        # self.calcTaskLevels()

    def getarray(self, index):
        return self.array[index]

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
        return self.deadline

    def setDeadline(self, deadline):
        self.deadline = deadline

    def getMaxParallel(self):
        return self.maxParallel

    def createMyDAXReader(self):
        return Workflow.MyDAXReader(self)

    class MyDAXReader(xml.sax.ContentHandler, object):

        def __init__(self, outer):
            self.__outer = outer
            self.__CurrentData = ""
            self.__tags = []
            self.__childId = ""
            self.__lastTask = None

        def startElement(self, uri, localName, qName, attrs):
            self.__CurrentData = qName
            if qName == "job":
                id = attrs["id"]
                if id in list(self.__outer.nameTaskMapping.keys()):
                    raise RuntimeError()
                t = Task(id, float(attrs["reuntime"]))
                self.__outer.nameTaskMapping[id] = t
                self.__lastTask = t
            elif qName == "uses" and self.__tags[len(self.__tags) - 1] == "job":
                # After reading the element "job", the element "uses" means a trasferData (i.e., data flow)
                filename = attrs["file"]
                fileSize = int(attrs["size"])
                td = self.__outer.transferData[filename]
                if td == None:
                    td = Workflow.TransferData(filename, fileSize)
                if attrs["link"] == "input":
                    td.addDestination(self.__lastTask)
                else:
                    td.setSource(self.__lastTask)
                self.__outer.transferData[filename] = td
            elif qName == "child":
                self.__childId = attrs["ref"]
            elif qName == "parent":
                # After reading the element "child", the element "parent" means an edge (i.e., control flow)
                child = self.__outer.nameTaskMapping[self.__childId]
                parent = self.__outer.nameTaskMapping[attrs["ref"]]

                e = Edge(parent, child)
                parent.insertOutEdge(e)
                child.insertInEdge(e)

            self.__tags.append(qName)

        def endElement(self, uri, localName, qName):
            tmp = self.__tags.pop()

    class TransferData:
        def __init__(self, name, size):
            self.__name = name
            self.__size = size
            self.__source = None
            self.__destinations = []

        def getSize(self):
            return self.__size

        def setSize(self, size):
            self.__size = size

        def getSource(self):
            return self.__source

        def setSource(self, source):
            self.__source = source

        def addDestination(self, t):
            self.__destinations.append(t)

        def getDestinations(self):
            return self.__destinations

        def __str__(self) -> str:
            return "TransferData [name=" + self.__name + ", size=" + self.__size + "]"
