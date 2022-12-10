import sys
import copy

sys.path.append('/Users/apple/Desktop/Create WS-ACO/MyCode')
from IaaSCloudWorkflowScheduler.WorkflowNode import WorkflowNode
from  IaaSCloudWorkflowScheduler.Resource import  Resource
# from ..WorkflowNode import WorkflowNode
# from ..Resource import Resource
from IaaSCloudWorkflowScheduler.ACO.CloudAcoResourceInstance import CloudAcoResourceInstance

# import warnings


class CloudAcoProblemNode:
    def __init__(self, node=None, resource=None, id=None):
        if node is not None:
            self.h = None
            self.setByRW = None
            self.__node = node
            # self.__defaultNode = WorkflowNode(node)
            self.__defaultNode = copy.deepcopy(node)
            self.__resource = resource
            self.__visited = False
            self.__id = id
        else:
            self.h = None
            self.setByRW = None
            self.__node = WorkflowNode("first")
            self.__defaultNode = WorkflowNode("first")
            self.__resource = CloudAcoResourceInstance(Resource(-1, 1, 1))
            self.__visited = False
            self.__id = -1

    def getNode(self):
        return self.__node

    def setUnvisited(self):
        self.__visited = False
        self.getNode().setUnscheduled()

    def resetNode(self):
        self.__node.setRunTime(self.__defaultNode.getRunTime())
        self.__node.setAFT(self.__defaultNode.getAFT())
        self.__node.setAST(0)
        # self.__node.setEST(self.__defaultNode.getEST())
        # self.__node.setEFT(self.__defaultNode.getEFT())
        # self.__node.setLFT(self.__defaultNode.getLFT())
        # self.__node.setLST(self.__defaultNode.getLST())
        self.__node.setUnscheduled()
        self.setUnvisited()

    def setNode(self, node):
        self.__node = node

    def getResource(self):
        return self.__resource

    def setResource(self, resource):
        self.__resource = resource

    def isVisited(self):
        return self.__visited

    def setVisited2(self):
        self.getNode().setScheduled()
        self.__visited = True

    def setVisited(self, environment):
        self.getNode().setScheduled()
        self.__visited = True
        if self.getNode().getId() == 'start':
            mxitr = len(environment.getProblemGraph().getInstanceSet().getInstances())
        else:
            mxitr = environment.getProblemGraph().getInstanceSet().getCount() * len(
                environment.getProblemGraph().getInstanceSet().getInstances())
        count = 0
        problemNodes = environment.getProblemGraph().getProblemNodeList()
        for node in problemNodes:
            if node.getNode().getId() == self.getNode().getId():
                node.setVisited2()
                count += 1
            if count >= mxitr:
                break

    def getId(self):
        return self.__id

    def setId(self, id):
        self.__id = id

    # warnings.filterwarnings("ignore")
    '''
    Getting the neighbor of every node.
    In this method we check the possible movement for ant.'''

    def getNeighbourhood(self, environment):
        finalNeighbours = []

        if environment.getProblemGraph().getNeighbours(self.getNode()) is None:
            finalNeighbours.append(environment.getProblemGraph().getStart())
            return finalNeighbours
        else:
            return environment.getProblemGraph().getNeighbours(self.getNode())

    def __str__(self):
        return "id:" + str(self.getId()) \
               + "node:" + str(self.getNode().getId()) \
               + " resource: " + str(self.getResource().getId()) \
               + " instance: " + str(self.getResource().getInstanceId()) \
               + " EST : " + str(self.getNode().getEST()) \
               + " AST : " + str(self.getNode().getAST()) \
               + " AFT : " + str(self.getNode().getAFT()) \
               + " LFT : " + str(self.getNode().getLFT()) \
               + " DL : " + str(self.getNode().getDeadline()) \
               + " H : " + str(self.h) \
               + " setByRW : " + str(self.setByRW)
