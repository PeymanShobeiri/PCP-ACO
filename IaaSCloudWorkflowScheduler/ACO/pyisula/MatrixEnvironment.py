from exception import InvalidInputException
import Environment

class MatrixEnvironment(Environment):

    def isProblemRepresentationValid(self):
        return True

    def __init__(self, problemRepresentation) :
        super().__init__()
        self.__problemRepresentation = problemRepresentation

        if not self.isProblemRepresentationValid():
            raise InvalidInputException("")
    
    def getProblemRepresentation(self):
        return self.__problemRepresentation
    
    def createPheromoneMatrix(self):
        pass

    def __str__(self):
        return "Problem Representation: Rows " + len(self.__problemRepresentation[0]) + " Columns " \
                + len(self.__problemRepresentation) + "\n" + "Pheromone Matrix: Rows "\
                + len(super().getPheromoneMatrix()[0])+ " Columns " + len(super().getPheromoneMatrix())