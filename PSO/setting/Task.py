import sys

sys.path.append('/Users/apple/Desktop/Create WS-ACO/MyCode')
from IaaSCloudWorkflowScheduler.Constants import Constants


class Task:
    def __init__(self, name, runtime):
        self.__internalId = 0
        self.__id = 0
        self.__name = ''
        self.__runtime = 0.0
        # self.__instructionSize = 0
        self.__outEdges = []
        self.__inEdges = []
        self.__topoCount = 0
        self.__bLevel = 0.0
        self.__tLevel = 0.0
        self.__sLevel = 0.0
        self.__ALAP = 0.0
        self.__pURank = 0.0
        self.__EST = -1
        self.__EFT = -1
        self.__LFT = -1
        self.__AST = -1
        self.__AFT = -1
        self.__criticalParent = None
        self.__isAssigned = False

        self.__id = self.__internalId
        self.__internalId += 1
        self.__name = name
        self.__runtime = runtime
        self.__instructionSize = (abs(float(runtime)) * float(Constants.STANDARD_MIPS))

    def resetInternalId(self):
        self.__internalId = 0

    def getId(self):
        return self.__id

    def getName(self):
        return self.__name

    def getbLevel(self):
        return self.__bLevel

    def setbLevel(self, bLevel):
        self.__bLevel = bLevel

    def gettLevel(self):
        return self.__tLevel

    def settLevel(self, tLevel):
        self.__tLevel = tLevel

    def getsLevel(self):
        return self.__sLevel

    def setsLevel(self, sLevel):
        self.__sLevel = sLevel

    def getALAP(self):
        return self.__ALAP

    def setALAP(self, aLAP):
        self.__ALAP = aLAP

    def getOutEdges(self):
        return self.__outEdges

    def getInEdges(self):
        return self.__inEdges

    def insertInEdge(self, e):
        if e.getDestination() != self:
            raise RuntimeError()
        self.__inEdges.append(e)

    def insertOutEdge(self, e):
        if e.getSource() != self:
            raise RuntimeError()
        self.__outEdges.append(e)

    def getInstructionSize(self):
        return self.__instructionSize

    def setInstructionSize(self, instructionSize):
        self.__instructionSize = instructionSize

    def getTopoCount(self):
        return self.__topoCount

    def setTopoCount(self, topoCount):
        self.__topoCount = topoCount

    def getpURank(self):
        return self.__pURank

    def setpURank(self, pURank):
        self.__pURank = pURank

    # ----------------overrides----------------

    def __str__(self):
        return "Task [id=" + self.__name + ", runtime=" + self.__runtime + "]"

    def getEST(self):
        return self.__EST

    def setEST(self, eST):
        self.__EST = eST

    def getEFT(self):
        return self.__EFT

    def setEFT(self, eFT):
        self.__EFT = eFT

    def getLFT(self):
        return self.__LFT

    def setLFT(self, lFT):
        self.__LFT = lFT

    def getCriticalParent(self):
        return self.__criticalParent

    def setCriticalParent(self, criticalParent):
        self.__criticalParent = criticalParent

    def isAssigned(self):
        return self.__isAssigned

    def setAssigned(self, isAssigned):
        self.__isAssigned = isAssigned

    def getAST(self):
        return self.__AST

    def setAST(self, aST):
        self.__AST = aST

    def getAFT(self):
        return self.__AFT

    def setAFT(self, aFT):
        self.__AFT = aFT

    # -------------comparators---------------
    class BLevelComparator:

        def make_comparator(g_than):
            def compare(x, y):
                if g_than(x, y):
                    return 1
                elif g_than(y, x):
                    return -1
                else:
                    return 0

            return compare

        def cmpValue(o1, o2):

            if o1.getbLevel() > o2.getbLevel() or o1.getName() == "entry" or o2.getName() == "exit":
                return True
            # elif o1.getName()=="exit" or o2.getName()=="entry":
            # return
            else:
                return False

    class PURankComparator:
        def make_comparator(g_than):
            def compare(x, y):
                if g_than(x, y):
                    return 1
                elif g_than(y, x):
                    return -1
                else:
                    return 0

            return compare

        def cmpValue(o1, o2):

            if o1.getpURank() > o2.getpURank() or o1.getName() == "entry" or o2.getName() == "exit":
                return True
            # elif o1.getName()=="exit" or o2.getName()=="entry":
            # return
            else:
                return False

    class TLevelComparator:
        def make_comparator(g_than):
            def compare(x, y):
                if g_than(x, y):
                    return 1
                elif g_than(y, x):
                    return -1
                else:
                    return 0

            return compare

        def cmpValue(o1, o2):

            if o1.gettLevel() > o2.gettLevel():
                return True
            elif o1.getName() == "exit" or o2.getName() == "entry":
                return True
            else:
                return False

    class ParallelComparator:
        def make_comparator(o1, o2):
            d1 = len(o1.getOutEdges()) - len(o1.getInEdges())
            d2 = len(o2.getOutEdges()) - len(o2.getInEdges())

            if d1 > d2:
                return -1
            elif d1 < d2:
                return 1
            else:
                return 0
