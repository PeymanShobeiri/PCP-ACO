from enum import Enum

class AntPolicyType(Enum):
    NODE_SELECTION = 0
    AFTER_NODE_SELECTION = 1
    AFTER_SOLUTION_IS_READY = 2