import Link


class WorkflowNode:
    def __init__(self, nodeId ,nodeName='',inSize=0 ,outSize=0 ,rt=0):
        self.__id = nodeId
        self.__name = nodeName
        self.__inputFileSize = inSize
        self.__outputFileSize = outSize
        self.__instructionSize = 0 # this is in MI units
        self.__runTime = rt
        self.__topologicaSortCount = 0
        self.__numPE = None   # what ?? 
        self.__parents = []         # both LINK type
        self.__children = []

        # for scheduling part 
        self.__scheduled = False
        self.__EST = None
        self.__EFT = None
        self.__AST = None # what is this ??
        self.__AFT = None
        self.__LFT = None
        self.__LST = None
        self.__MET = None
        self.__upRank = None
        self.__subDeadline = None
        self.__selectedResource = -1
    
    def getTopologicaSortCount(self):
        return self.__topologicaSortCount
    
    def setTopologicaSortCount(self,topologicaSortCount):
        self.__topologicaSortCount = topologicaSortCount
    
    def getId(self):
        return self.__id

    def getName(self):
        return self.__name

    def setName(self, newName):
        self.__name = newName

    def getInputFileSize(self):
        return self.__inputFileSize

    def setInputFileSize(self ,newSize):
        if newSize >= 0 :
            self.__inputFileSize = newSize
    
    def getOutputFileSize(self):
        return self.__outputFileSize
    
    def setOutputFileSize(self, newSize):
        if newSize >= 0:
            self.__outputFileSize = newSize

    def getRunTime(self):
        return self.__runTime

    def setRunTime(self, newRunTime):
        if newRunTime >= 0:
            self.__runTime = newRunTime

    def getNumPE(self):
        return self.__numPE
    
    def setNumPE(self , n):
        self.__numPE = n 

    def addParent(self, parentId, size):
        newLink = Link(parentId,size)
        self.__parents.append(newLink)

    def addChild(self, childId, size):
        newLink = Link(childId,size)
        self.__children.append(newLink)

    def getParents(self):
        return self.__parents
    
    def getChildren(self):
        return self.__children
    
    def hasChild(self):
        if len(self.__children) == 0:
            return False
        else: 
            return True
    
    def hasParent(self):
        if len(self.__parents) == 0:
            return False
        else: 
            return True
    
    def isScheduled(self):
        return self.__scheduled

    def setScheduled(self):
        self.__scheduled = True
    
    def setUnscheduled(self):
        self.__scheduled = False
    
    def getEST(self):
        return self.__EST
    
    def setEST(self, EST):
        self.__EST = EST
    
    def getEFT(self):
        return self.__EFT

    def setEFT(self, EFT): 
        self.__EFT = EFT
    
    def getAST(self):
        return self.__AST
    
    def setAST(self, AST):
        self.__AST = AST
    
    def getAFT(self):
        return self.__AFT
        
    def setAFT(self,AFT):
        self.__AFT = AFT
    
    def getLFT(self):
        return self.__LFT
    
    def setLFT(self ,LFT):
        self.__LFT = LFT
    
    def getLST(self):
        return self.__LST
    
    def setLST(self, LST):
        self.__LST = LST

    def getSelectedResource(self):
        return self.__selectedResource
    
    def setSelectedResource(self, resIndex):
        self.__selectedResource = resIndex
    
    def getMET(self):
        return self.__MET
    
    def setMET(self, time):
        self.__MET = time
    
    def getInstructionSize(self):
        return self.__instructionSize
    
    def setInstructionSize(self, size):
        self.__instructionSize = size
    
    def getUpRank(self):
        return self.__upRank
    
    def setUpRank(self, ur):
        self.__upRank = ur

    def getDeadline(self):
        return self.__subDeadline
    
    def setDeadline(self, d):
        self.__subDeadline = d
    
    def getChildDataSize(self, childId):
        for child in self.__children:
            if child.getId() == childId:
                return child.getDataSize()
        return 0
    
    def getParentDataSize(self, parentId):
        for parent in self.__parents:
            if parent.getId() == parentId:
                return parent.getDataSize()
        return 0