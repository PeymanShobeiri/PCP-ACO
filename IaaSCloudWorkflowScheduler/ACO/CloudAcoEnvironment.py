import sys
import numpy as np

sys.path.append('/Users/apple/Desktop/Create WS-ACO/MyCode')
from IaaSCloudWorkflowScheduler.ACO.pyisula.Environment import Environment
from IaaSCloudWorkflowScheduler.ACO.CloudAcoProblemRepresentation import CloudAcoProblemRepresentation


class CloudAcoEnvironment(Environment):

    def __init__(self, problemGraph=None, problemRepresentation=None):
        if problemRepresentation is not None:
            self.problemGraph = None
            super().__init__(problemRepresentation)
        else:
            self.problemGraph = problemGraph
            # tmp = np.full([100, 100], 0.0)
            # tmp = []
            # for row in range(100):
            #     tmp.append([float(0) for x in range(100)])
            # super().__init__(tmp)

            # self.setPheromoneMatrix(self.createPheromoneMatrix())
            # self.populatePheromoneMatrix(0.01)

    def createPheromoneMatrix(self):
        if self.problemGraph is None:
            cur = np.full([100, 100], 0.0)
            # cur = []
            # for row in range(100):
            #     cur.append([float(0) for x in range(100)])
            return cur

        ret = np.full([len(self.problemGraph.getProblemNodeList()), len(self.problemGraph.getProblemNodeList())], 0.0)
        # ret = []
        # for row in range(len(self.problemGraph.getProblemNodeList())):
        #     ret.append([float(0) for x in range(len(self.problemGraph.getProblemNodeList()))])
        return ret

    def getPheromoneValues(self):
        a = []
        size = self.getProblemGraph().getGraphSize()
        for i in range(size):
            for j in range(size):
                if a not in self.getPheromoneMatrix()[i][j]:
                    a.append(self.getPheromoneMatrix()[i][j])
        return a

    def getProblemGraph(self) -> CloudAcoProblemRepresentation:
        return self.problemGraph
