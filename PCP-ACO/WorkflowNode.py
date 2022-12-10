from Link import Link


class WorkflowNode:
    def __init__(self, nodeId, nodeName='', inSize=0, outSize=0, rt=0):

        # print(type(nodeId))
        if type(nodeId) == str:
            self.id = nodeId
            self.matrixid = None
            self.name = nodeName
            self.inputFileSize = inSize
            self.outputFileSize = outSize
            self.instructionSize = 0  # this is in MI units
            self.runTime = rt
            self.topologicaSortCount = 0
            self.DAG_level = 0
            self.numPE = None
            self.parents = []  # both LINK type
            self.children = []

            # for scheduling part
            self.scheduled = False
            self.EST = None
            self.EFT = None
            self.AST = None
            self.AFT = None
            self.LFT = None
            self.LST = None
            self.MET = None
            self.upRank = None
            self.subDeadline = None
            self.selectedInstance = -1
            self.selectedResource = -1
        else:
            self.id = nodeId.id
            self.matrixid = nodeId.matrixid
            self.name = nodeId.name
            self.inputFileSize = nodeId.inputFileSize
            self.outputFileSize = nodeId.outputFileSize
            self.runTime = nodeId.runTime
            self.topologicaSortCount = 0
            self.DAG_level = nodeId.getDAG_level()
            self.numPE = None
            self.instructionSize = nodeId.instructionSize
            self.scheduled = nodeId.scheduled
            self.EST = nodeId.EST
            self.EFT = nodeId.EFT
            self.LST = nodeId.LST
            self.AST = nodeId.AST
            self.AFT = nodeId.AFT  # needed ?
            self.LFT = nodeId.LFT
            self.MET = nodeId.MET
            self.upRank = nodeId.upRank
            self.subDeadline = nodeId.subDeadline
            self.selectedInstance = nodeId.selectedInstance
            self.selectedResource = nodeId.selectedResource
            self.parents = []
            for l in nodeId.parents:
                self.parents.append(Link(l.getId(), l.getDataSize()))
            self.children = []
            for l in nodeId.children:
                self.children.append(Link(l.getId(), l.getDataSize()))

    def getMatrixId(self):
        return self.matrixid

    def setMatrixId(self, id):
        self.matrixid = id

    def setSelectedInstance(self,ins):
        self.selectedInstance = ins

    def getSelectedInstance(self):
        return self.selectedInstance

    def getTopologicaSortCount(self):
        return self.topologicaSortCount

    def getNeighbourhood(self, environment):
        return environment.getProblemGraph().getNeighbours(self)

    def getDAG_level(self):
        return self.DAG_level

    def setDAG_level(self, n):
        self.DAG_level = n

    def setTopologicaSortCount(self, topologicaSortCount):
        self.topologicaSortCount = topologicaSortCount

    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def getInputFileSize(self):
        return self.inputFileSize

    def setInputFileSize(self, newSize):
        if newSize >= 0:
            self.inputFileSize = newSize

    def getOutputFileSize(self):
        return self.outputFileSize

    def setOutputFileSize(self, newSize):
        if newSize >= 0:
            self.outputFileSize = newSize

    def getRunTime(self):
        return self.runTime

    def setRunTime(self, newRunTime):
        if newRunTime >= 0:
            self.runTime = newRunTime

    def getNumPE(self):
        return self.numPE

    def setNumPE(self, n):
        self.numPE = n

    def addParent(self, parentId, size):
        newLink = Link(parentId, size)
        self.parents.append(newLink)

    def addChild(self, childId, size):
        newLink = Link(childId, size)
        self.children.append(newLink)

    def getParents(self):
        return self.parents

    def getChildren(self):
        return self.children

    def hasChild(self):
        if len(self.children) == 0:
            return False
        else:
            return True

    def hasParent(self):
        if len(self.parents) == 0:
            return False
        else:
            return True

    def isScheduled(self):
        return self.scheduled

    def setScheduled(self):
        self.scheduled = True

    def setUnscheduled(self):
        self.scheduled = False

    def getEST(self):
        return self.EST

    def setEST(self, EST):
        self.EST = EST

    def getEFT(self):
        return self.EFT

    def setEFT(self, EFT):
        self.EFT = EFT

    def getAST(self):
        return self.AST

    def setAST(self, AST):
        self.AST = AST

    def getAFT(self):
        return self.AFT

    def setAFT(self, AFT):
        self.AFT = AFT

    def getLFT(self):
        return self.LFT

    def setLFT(self, LFT):
        self.LFT = LFT

    def getLST(self):
        return self.LST

    def setLST(self, LST):
        self.LST = LST

    def getSelectedResource(self):
        return self.selectedResource

    def setSelectedResource(self, resIndex):
        self.selectedResource = resIndex

    def getMET(self):
        return self.MET

    def setMET(self, time):
        self.MET = time

    def getInstructionSize(self):
        return self.instructionSize

    def setInstructionSize(self, size):
        self.instructionSize = size

    def getUpRank(self):
        return self.upRank

    def setUpRank(self, ur):
        self.upRank = ur

    def getDeadline(self):
        return self.subDeadline

    def setDeadline(self, d):
        self.subDeadline = d

    def getChildDataSize(self, childId):
        for child in self.children:
            if child.getId() == childId:
                return child.getDataSize()
        return 0

    def getParentDataSize(self, parentId):
        for parent in self.parents:
            if parent.getId() == parentId:
                return parent.getDataSize()
        return 0
