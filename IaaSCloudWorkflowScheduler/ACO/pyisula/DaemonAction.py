import sys
sys.path.append('/Users/apple/Desktop/Create WS-ACO/MyCode')

from IaaSCloudWorkflowScheduler.ACO.pyisula.Environment import Environment
from abc import ABC,abstractmethod


class DaemonAction(ABC, Environment):
    def __init__(self,acoPhase):
        super().__init__()
        self.__acoPhase = acoPhase
        self.__environment = None
        self.__antColony = None
        self.__problemSolver = None
    
    def getAcoPhase(self):
        return self.__acoPhase

    def getEnvironment(self):
        return self.__environment
    
    def setEnvironment(self, environment):
        self.__environment = environment

    def getAntColony(self):
        return self.__antColony
    
    def setAntColony(self, antColony):
        self.__antColony = antColony
    
    def getProblemSolver(self):
        return self.__problemSolver
    
    def setProblemSolver(self, problemSolver):
        self.__problemSolver = problemSolver
    
    @abstractmethod
    def applyDaemonAction(self, configurationProvider):
        pass
