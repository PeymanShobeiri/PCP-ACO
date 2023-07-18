import sys
from DAG.Adag import Adag
from DAG.DagUtils import DagUtils
from Constants import Constants
from WorkflowGraph import WorkflowGraph
from ResourceSet import ResourceSet
from Resource import Resource
from FastestPolicy import FastestPolicy
from CheapestPolicy import CheapestPolicy
from PcpPolicy2 import PcpPolicy2
from PcpD2Policy2 import PcpD2Policy2


class WorkflowBroker:

    def createResourceList(self):
        self.resources = ResourceSet(self.interval)
        self.resources.addResource(Resource(0, 1, 500))
        self.resources.addResource(Resource(1, 0.855, 450))
        self.resources.addResource(Resource(2, 0.72, 400))
        self.resources.addResource(Resource(3, 0.595, 350))
        self.resources.addResource(Resource(4, 0.48, 300))
        self.resources.addResource(Resource(5, 0.375, 250))
        self.resources.addResource(Resource(6, 0.28, 200))
        self.resources.addResource(Resource(7, 0.195, 150))
        self.resources.addResource(Resource(8, 0.12, 100))
        # self.resources.addResource(Resource(9, 0.8, 20))
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

        if type == "Fastest":
            self.policy = FastestPolicy(self.graph, self.resources, self.bandwidth)
        elif type == "Cheapest":
            self.policy = CheapestPolicy(self.graph, self.resources, self.bandwidth)
        elif type == "IC_PCP2":
            self.policy = PcpPolicy2(self.graph, self.resources, self.bandwidth)
        elif type == "PCP_ACO":
            self.policy = PcpD2Policy2(self.graph, self.resources, self.bandwidth)

    def schedule(self, startTime, deadline, ICPCP) -> float:
        tmp = self.policy.schedule(startTime, deadline, ICPCP)
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
