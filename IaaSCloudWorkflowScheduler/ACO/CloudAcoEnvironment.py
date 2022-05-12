import sys

sys.path.append('/Users/apple/Desktop/Create WS-ACO/MyCode')
from IaaSCloudWorkflowScheduler.ACO.pyisula.Environment import Environment


class CloudAcoEnvironment(Environment):

    def __init__(self, problemGraph=None, problemRepresentation=None):
        super().setPheromoneMatrix = problemRepresentation
        super().__init__(100)
        self.problemGraph = problemGraph
        self.setPheromoneMatrix(self.createPheromoneMatrix())
        self.populatePheromoneMatrix(0.01)

    def createPheromoneMatrix(self):
        if self.problemGraph == None:
            return super()._init_matrix(100)
        return super()._init_matrix(len(self.problemGraph.getProblemNodeList))

    def getProblemGraph(self):
        return self.problemGraph

    def getPheromoneValues(self):
        a = []
        size = self.getProblemGraph().getGraphSize()
        for i in range(size):
            for j in range(size):
                if a not in self.getPheromoneMatrix()[i][j]:
                    a.append(self.getPheromoneMatrix()[i][j])
        return a
