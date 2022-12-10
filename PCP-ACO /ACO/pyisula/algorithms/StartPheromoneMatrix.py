from ..Environment import Environment
from ..DaemonAction import DaemonAction
from ..DaemonActionType import DaemonActionType
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)


class StartPheromoneMatrix(DaemonAction):
    def __init__(self):
        super().__init__(DaemonActionType().INITIAL_CONFIGURATION)
    
    def getInitialPheromoneValue(self, configurationProvider):
        return configurationProvider.getInitialPheromoneValue()
    

    def applyDaemonAction(self, configurationProvider):
        logger.info("INITIALIZING PHEROMONE MATRIX")

        initialPheromoneValue = self.getInitialPheromoneValue(configurationProvider)
        if initialPheromoneValue == 0.0:
            logger.warning("An initial pheromone value of zero can affect the node selection process.")
        
        logger.info("Initial pheromone value: " + initialPheromoneValue)

        self.getEnvironment().populatePheromoneMatrix(initialPheromoneValue)
        logger.info("Pheromone matrix after initilizatation :" + self.getEnvironment().getPheromoneMatrix())

    def __str__(self) :
        return "StartPheromoneMatrix{}"


