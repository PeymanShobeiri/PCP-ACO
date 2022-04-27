#from IaaSCloudWorkflowScheduler.Constants import Constants
#from IaaSCloudWorkflowScheduler import Constants
#from ...IaaSCloudWorkflowScheduler.Constants import Constants
import sys
sys.path.append('/Users/apple/Desktop/Create WS-ACO/MyCode')
from IaaSCloudWorkflowScheduler.Constants import Constants


class VM:
    #def __init__(self,type) :
    LAUNCH_TIME = 0
    NETWORK_SPEED = Constants.BANDWIDTH
    TYPE_NO = 10
    SPEEDS = [1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.25, 0.2]
    MIPS = [100, 90, 80, 70, 60, 50, 40, 30, 25, 20]
    UNIT_COSTS = [20, 16.2, 12.8, 9.8, 7.2, 5, 3.2, 1.8, 1.25, 0.8]

    INTERVAL = 3600

    FASTEST = 0
    SLOWEST = 9

    internalId = 0
    id = 0
    type = 0

    def __init__(self, type):
        self.type = type
        self.id = self.internalId
        self.internalId += 1


    def resetInternalId(self):
        self.internalId = 0
    
    def getMIPS(self):
        return float(self.MIPS[self.type])
    
    def getUnitCost(self):
        return self.UNIT_COSTS[self.type]
    
    def getId(self):
        return self.id
    
    def getType(self):
        return self.type
    
    def setType(self, type):
        self.type = type
    
    def __str__(self) :
        return "VM [id=" + self.id + ", type=" + self.type + "]"

