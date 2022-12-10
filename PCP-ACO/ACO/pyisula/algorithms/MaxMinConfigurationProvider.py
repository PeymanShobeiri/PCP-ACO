from ..ConfigurationProvider import ConfigurationProvider
import zope.interface


class MaxMinConfigurationProvider(ConfigurationProvider, zope.interface.Interface):

    def MaxMinConfigurationProvider(self):
        pass

    def getMinimumPheromoneValue(self):
        pass
