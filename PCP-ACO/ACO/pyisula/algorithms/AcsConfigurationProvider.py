
import zope.interface
from ..ConfigurationProvider import ConfigurationProvider

class AcsConfigurationProvider(zope.interface.Interface , ConfigurationProvider):

    def getBestChoiceProbability(self):
        pass
    
    def getPheromoneDecayCoefficient(self):
        pass
    

