from IaaSCloudWorkflowScheduler.ACO.CloudAcoProblemRepresentation import CloudAcoProblemRepresentation
from ..Resource import Resource
from .pyisula.Ant import Ant
from .pyisula.ConfigurationProvider import ConfigurationProvider
from .CloudAcoProblemNode import CloudAcoProblemNode
from .CloudAcoWorkflow import CloudAcoWorkflow

import sys
#CloudAcoWorkflow().antId + 1

class CloudAcoAntForWorkflow(Ant):

    def __init__(self , environment):
        self.__currentNode = CloudAcoProblemNode()
        self.__environment = environment
        self.__id =CloudAcoWorkflow.antId + 1
        self.__lastSolutionCost = 0
        self.__lastMakeSpan = 0
        self.__lastRawSolutionCost = 0
        self.__validAnswer = False
        self.__heuristicCache = {}
        self.__lastNodeId = -1
        self.__cacheUses = 0
        self.setSolution(CloudAcoProblemNode(environment.getProblemGraph().getGraphSize()))  # [] ?? 
        self.setVisited({})
        if self.__heuristicCache == None:
            self.__heuristicCache = {}

    def getLastMakeSpan(self):
        return self.__lastMakeSpan
    
    def setLastMakeSpan(self, lastMakeSpan):
        self.__lastMakeSpan = lastMakeSpan
    
    def isSolutionReady(self, cloudAcoEnvironment):
        return self.getCurrentIndex() == self.__environment.getProblemGraph().getGraphSize()
    
    def getSolutionCost(self, cloudAcoEnvironment):
        total = 0.0
        deadline = self.__environment.getProblemGraph().getDeadline()

        tmp = self.__environment.getProblemGraph().getInstanceSet().getInstances()
        helper = [i.getTotalCost() for i in tmp.values]
        total = sum(helper)

        self.__lastSolutionCost = total
        self.__lastRawSolutionCost = total
        self.__lastMakeSpan = self.__environment.getProblemGraph().getGraph().getNodes().get(self.__environment.getProblemGraph().getGraph().getEndId()).getAFT()
        if self.__environment.getProblemGraph().getGraph().getNodes().get(self.__environment.getProblemGraph().getGraph().getEndId()).getAFT() > deadline:
            self.__validAnswer = False
            self.__lastSolutionCost = total * (self.__environmentgetProblemGraph().getGraph().getNodes().get(self.__environment.getProblemGraph().getGraph().getEndId()).getAFT() - deadline)
            return self.__lastSolutionCost
        
        return total
    
    def getLastSolutionCost(self):
        return self.__lastSolutionCost

    def getLastRawSolutionCost(self):
        return self.__lastRawSolutionCost
    
    def isValidAnswer(self):
        for n in self.getSolution():
            if n == None:
                return False
        
        return self.__validAnswer and self.isSolutionReady(self.__environment)
    
    def setValidAnswer(self, validAnswer):
        self.__validAnswer = validAnswer
    
    def getSolutionAsString(self):
        tmp = self.__environment.getProblemGraph().getInstanceSet().getInstances()
        helper = [i.getTotalCost() for i in tmp.values]
        total = sum(helper)

        deadline = self.__environment.getProblemGraph().getDeadline()
        headersList = ["N", "R", "I", "I-cost", "R-cost", "AST", "runtime", "AFT", "SD", "LFT", "I-start", "H"]
        rowsList = []

        # bookmark 1

        for node in self.getSolution():
            if node == None:
                continue
                
            runtime = node.getResource().getTaskDuration(node.getNode())
            tmp2 = []
            tmp2.append(str(node.getNode().getId()))
            tmp2.append(str(node.getResource().getId()))
            tmp2.append(str(node.getResource().getInstanceId()))
            tmp2.append(str(node.getResource().getTotalCost()))
            tmp2.append(str(node.getResource().getResource().getCost()))
            tmp2.append(str(node.getNode().getAST()))
            m = min(4, len(str(runtime)))
            string = str(runtime)
            tmp2.append(string[0:m])
            tmp2.append(str(node.getNode().getAFT()))
            tmp2.append(str(node.getNode().getDeadline()))
            tmp2.append(str(node.getNode().getLFT()))
            tmp2.append(str(node.getResource().getInstanceStartTime()))
            x = min(4, len(str(runtime)))
            string2 = str(node.h)
            tmp2.append(string2[0:x])

            rowsList.append(tmp2)
        
        # create a board  !!!!!!!!!!!!!!!!
        rowsList.append(total)
        rowsList.append(deadline)
        return rowsList
    
    def resetCache(self):
        print("cache size:" + len(self.__heuristicCache) + " uses time:" + self.__cacheUses + " ario:" ,end=' ' )
        if self.__cacheUses + len(self.__heuristicCache) == 0:
            print(0)
        else:
            print(self.__cacheUses / len(self.__heuristicCache))
        
        self.__cacheUses = 0
        self.__heuristicCache.clear()
    
    def getNeighbourhood(self, cloudAcoEnvironment):
        return self.__currentNode.getNeighbourhood(cloudAcoEnvironment)
    
    def getPheromoneTrailValue(self, next, positionInSolution, cloudAcoEnvironment):
        if self.__currentNode.getId() == CloudAcoProblemRepresentation().START_NODE_ID:
            return CloudAcoProblemRepresentation().START_NODE_PHEROMONE
        
        pheromoneMatrix = self.__environment.getPheromoneMatrix()
        return pheromoneMatrix[self.__currentNode.getId()][next.getId()]
    
    def visitNode(self, visitedNode):
        if self.getCurrentIndex() > len(self.getSolution()):
            self.getSolution()[self.getCurrentIndex()] = visitedNode
            visitedNode.getResource().setCurrentTask(visitedNode)
            visitedNode.getNode().setRunTime(visitedNode.getResource().getTaskDuration(visitedNode.getNode()))
            self.__environment.getProblemGraph().updateChildrenEST(visitedNode.getNode())
            self.getVisited()[visitedNode] = True
            self.__currentNode = visitedNode
            self.setCurrentIndex(self.getCurrentIndex() + 1)

    def setUnvisited(self):
        self.__environment.getProblemGraph().resetNodes()
        self.__currentNode.setUnvisited()
        self.__currentNode = self.__environment.getProblemGraph().getStartNode()
        self.getVisited().clear()
        self.__environment.getProblemGraph().getInstanceSet().resetPerAnt()


    def clear(self):
        self.setCurrentIndex(0)
        if self.getSolution() != None:
            for i in range(len(self.getSolution())):
                self.getSolution()[i] = None
            
            self.setUnvisited()
        
    def doAfterSolutionIsReady(self, environment, configurationProvider):
        self.doAfterSolutionIsReady(environment, configurationProvider)
        self.setUnvisited()
    
    class HeuristicCondition:
        def __init__(self, curDuration , curCost , curStartTime, instanceId) :
            self.__curDuration = curDuration
            self.__curCost = curCost
            self.__curStartTime = curStartTime
            self.__instanceId = instanceId
        
        def getCurDuration(self):
            return self.__curDuration
        
        def setCurDuration(self, curDuration):
            self.__curDuration = curDuration
        
        def getCurCost(self):
            return self.__curCost
        
        def setCurCost(self, curCost):
            self.__curCost = curCost
        
        def getCurStartTime(self):
            return self.__curStartTime
        
        def setCurStartTime(self, curStartTime):
            self.__curStartTime = curStartTime
        
        def getInstanceId(self):
            return self.__instanceId
        
        def setInstanceId(self, instanceId):
            self.__instanceId = instanceId
        
        def __eq__(self, other):
            if self == other:
                return True
            if type(other) != type(self):
                return False
            if (self.__curDuration == other.__curDuration) and (self.__curCost == other.__curCost) and (self.__curStartTime == other.__curStartTime) and (self.__instanceId == other.__instanceId):
                return True
            else:
                return False

        def hashCode(self):     
            #  return Objects.hash(curDuration, curCost, curStartTime, instanceId);
            return hash(self)


    def getHeuristicValue(self, destination, positionInSolution, cloudAcoEnvironment):
        curCost = destination.getResource().getCost(destination.getNode())
        currentDuration = destination.getResource().getTaskDuration(destination.getNode())
        currentST = max(destination.getResource().getInstanceReleaseTime(), destination.getNode().getEST())
        currentFT = currentST + currentDuration

        hc = self.HeuristicCondition(currentDuration, curCost, currentST, destination.getResource().getId())
        if hc in self.__heuristicCache.keys():
            self.__cacheUses += 1
            return self.__heuristicCache.get(hc)
        
        h1 = 0.0
        h2 = 0.0
        
        if not (destination.getNode().getId()).lower() == "end" and (not (destination.getNode().getId()).lower() == "start"):
            if currentFT > destination.getNode().getLFT():
                return 0.0
        
        bad = False

        if currentFT < destination.getNode().getDeadline():
            h1 = 1
        else:
            h1 = max(0, (((destination.getNode().getLFT() - currentFT) + 1) / ((destination.getNode().getLFT() - destination.getNode().getDeadline() + 1) * 1.0)))
            bad = True
        
        maxCost = -1
        minCost = sys.maxsize
        fastest = sys.maxsize
        slowest = 0
        temp = 0.0
        tempDuration = 0.0

        for entry in self.__environment.getProblemGraph().getInstanceSet().getInstances():
            for instance in entry.getValue():
                temp = instance.getCost(destination.getNode())
                tempDuration = instance.getTaskDuration(destination.getNode())
                if temp > maxCost:
                    maxCost = temp
                elif temp < minCost:
                    minCost = temp
        
        h3 = (slowest - currentDuration + 1) / (slowest - fastest + 1)

        h2 = ((maxCost - curCost + 1) / (maxCost - minCost + 1))
        p1 = 5
        p2 = 5
        p3 = 5
        ratio = p1 + p2 + p3

        if positionInSolution < ((self.__environment.getProblemGraph().getGraphSize()) / 3):
            p1 = 2
            p2 = 11
            p3 = 2
        elif positionInSolution > (2 * (self.__environment.getProblemGraph().getGraphSize() / 3)):
            p1 = 2
            p2 = 11
            p3 = 2
        
        result = ((h1 * p1) + (h2 * p2) + (h3 * p3)) / ratio

        if bad :
            result = pow(result, 2)
        self.__heuristicCache[hc] = result
        return result



