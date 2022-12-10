from abc import ABC, abstractmethod

from Environment import Environment


class AntPolicy(ABC, Environment):
    def __init__(self):
        super().__init__()
        self.__policyType = None
        self.__ant = None

    def AntPolicy(self, antPhase):
        self.__policyType = antPhase

    def getPolicyType(self):
        return self.__policyType

    def setAnt(self, ant):
        self.__ant = ant

    def getAnt(self):
        return self.__ant

    @abstractmethod
    def applyPolicy(self, environment, configurationProvider):
        pass
