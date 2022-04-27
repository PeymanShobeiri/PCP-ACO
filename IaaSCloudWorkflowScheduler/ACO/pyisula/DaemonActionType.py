from enum import Enum

class DaemonActionType(Enum):
    INITIAL_CONFIGURATION = 0
    AFTER_ITERATION_CONSTRUCTION = 1