import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)


class Environment:
    def _init_matrix(self, size, value=0.0):
        ret = []
        for row in range(size):
            ret.append([float(value) for x in range(size)])
        return ret

    def __init__(self, size, value=0.0):
        self.pheromoneMatrix = self._init_matrix(size, value)

    def setPheromoneMatrix(self, pheromoneMatrix):
        self.pheromoneMatrix = pheromoneMatrix

    def getPheromoneMatrix(self):
        return self.pheromoneMatrix

    def populatePheromoneMatrix(self, pheromoneValue):  # just don't use it :) 
        if self.pheromoneMatrix == None or len(self.pheromoneMatrix) == 0:
            raise ValueError("The pheromone matrix is not properly configured. Verify the implementation of " +
                             "the createPheromoneMatrix() method.")
        matrixRows = len(self.pheromoneMatrix)
        matrixColumns = len(self.pheromoneMatrix[0])
        for i in range(matrixRows):
            for j in range(matrixColumns):
                self.pheromoneMatrix[i][j] = pheromoneValue

    def applyFactorToPheromoneMatrix(self, factor):
        matrixRows = len(self.pheromoneMatrix)
        matrixColumns = len(self.pheromoneMatrix[0])

        for i in range(matrixRows):
            for j in range(matrixColumns):
                newValue = self.pheromoneMatrix[i][j] * factor
                self.pheromoneMatrix[i][j] = newValue
