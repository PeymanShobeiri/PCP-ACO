import sys
from DAG.Adag import Adag
from DAG.DagUtils import DagUtils
from Constants import Constants
from WorkflowGraph import WorkflowGraph
from ResourceSet import ResourceSet
from Resource import Resource
from ScheduleType import ScheduleType
from FastestPolicy import FastestPolicy
from CheapestPolicy import CheapestPolicy
from PcpPolicyInsertion import PcpPolicyInsertion
from PcpD2Policy import PcpD2Policy
from ListPolicy2 import ListPolicy2
from PcpPolicy2 import PcpPolicy2
from PcpD2Policy2 import PcpD2Policy2
from ListPolicy3 import ListPolicy3
from ICLossPolicy2 import ICLossPolicy2

class WorkflowBroker:

    def createResourceList(self):
        self.resources = ResourceSet(self.interval)

        self.resources.addResource(Resource(0, 20, 100))
        self.resources.addResource(Resource(1, 16.2, 90))
        self.resources.addResource(Resource(2, 12.8, 80))
        self.resources.addResource(Resource(3, 9.8, 70))
        self.resources.addResource(Resource(4, 7.2, 60))
        self.resources.addResource(Resource(5, 5, 50))
        self.resources.addResource(Resource(6, 3.2, 40))
        self.resources.addResource(Resource(7, 1.8, 30))
        self.resources.addResource(Resource(8, 1.25, 25))
        self.resources.addResource(Resource(9, 0.8, 20))
        self.resources.sort()

    def __init__(self, wfDescFile, type):
        self.interval = 3600
        self.bandwidth = Constants.BANDWIDTH
        self.graph = None
        self.resources = None
        self.policy = None

        dag = None
        try:
            dag = DagUtils.readWorkflowDescription(wfDescFile)
        except Exception as e:
            print("Error reading Workflow File " + '  ' + str(e))

        self.graph = WorkflowGraph()
        self.graph.convertDagToWorkflowGraph(dag)
        self.createResourceList()

        if type == ScheduleType.Fastest:
            self.policy = FastestPolicy(self.graph, self.resources, self.bandwidth)
        elif type == ScheduleType.Cheapest:
            self.policy = CheapestPolicy(self.graph, self.resources, self.bandwidth)
        elif type == ScheduleType.IC_PCP:
            self.policy = PcpPolicyInsertion(self.graph, self.resources, self.bandwidth)
        elif type == ScheduleType.IC_PCPD2:
            self.policy = PcpD2Policy(self.graph, self.resources, self.bandwidth)
        elif type == ScheduleType.List:
            self.policy = ListPolicy2(self.graph, self.resources, self.bandwidth)
        elif type == ScheduleType.IC_PCP2:
            self.policy = PcpPolicy2(self.graph, self.resources, self.bandwidth)
        elif type == ScheduleType.IC_PCPD2_2:
            self.policy = PcpD2Policy2(self.graph, self.resources, self.bandwidth)
        elif type == ScheduleType.List2:
            self.policy = ListPolicy3(self.graph, self.resources, self.bandwidth)
        elif type == ScheduleType.IC_Loss:
            self.policy = ICLossPolicy2(self.graph, self.resources, self.bandwidth)

    def schedule(self, startTime, deadline) -> float:
        tmp = self.policy.schedule(startTime, deadline)
        return tmp

    def getGraph(self):
        return self.graph

    def setGraph(self, graph):
        self.graph = graph

    def getResources(self):
        return self.resources

    def setResources(self, resources):
        self.resources = resources

    def getPolicy(self):
        return self.policy

    def setPolicy(self, policy):
        self.policy = policy

    def getInterval(self):
        return self.interval

    def getBandwidth(self):
        return self.bandwidth
