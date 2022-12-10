import logging
from abc import abstractmethod
import numpy as np

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)


class Environment:
    """def _init_matrix(self, size, value=0.0):
        ret = []
        for row in range(size):
            ret.append([float(value) for x in range(size)])
        return ret"""

    def __init__(self, problemRepresentation):
        self.problemRepresentation = problemRepresentation
        self.pheromoneMatrix = self.createPheromoneMatrix()

        if not self.isProblemRepresentationValid():
            raise Exception("invalid input ")

    @abstractmethod
    def createPheromoneMatrix(self):
        pass

    def isProblemRepresentationValid(self):
        return True

    def getProblemRepresentation(self):
        return self.problemRepresentation

    def setPheromoneMatrix(self, pheromoneMatrix):
        self.pheromoneMatrix = pheromoneMatrix

    def getPheromoneMatrix(self):
        return self.pheromoneMatrix

    def populatePheromoneMatrix(self, pheromoneValue):
        if self.pheromoneMatrix is None or len(self.pheromoneMatrix) == 0:
            raise ValueError("The pheromone matrix is not properly configured. Verify the implementation of " +
                             "the createPheromoneMatrix() method.")

        self.pheromoneMatrix = np.full([len(self.pheromoneMatrix), len(self.pheromoneMatrix[0])], pheromoneValue)

        # matrixRows = len(self.pheromoneMatrix)
        # matrixColumns = len(self.pheromoneMatrix[0])
        # for i in range(matrixRows):
        #     for j in range(matrixColumns):
        #         self.pheromoneMatrix[i][j] = pheromoneValue

    def __str__(self):
        return "Problem Representation: Rows " + str(len(self.problemRepresentation)) + " Columns " \
                + str(len(self.problemRepresentation[0])) + "\n" + "Pheromone Matrix: Rows " \
                + str(len(self.pheromoneMatrix)) + " Columns " + str(len(self.pheromoneMatrix[0]))

    def applyFactorToPheromoneMatrix(self, factor):

        self.pheromoneMatrix = self.pheromoneMatrix * factor
        # matrixRows = len(self.pheromoneMatrix)
        # matrixColumns = len(self.pheromoneMatrix[0])
        #
        # for i in range(matrixRows):
        #     for j in range(matrixColumns):
        #         newValue = self.pheromoneMatrix[i][j] * factor
        #         self.pheromoneMatrix[i][j] = newValue
