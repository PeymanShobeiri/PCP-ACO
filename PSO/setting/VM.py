#from IaaSCloudWorkflowScheduler.Constants import Constants
#from IaaSCloudWorkflowScheduler import Constants
#from ...IaaSCloudWorkflowScheduler.Constants import Constants
import sys
sys.path.append('/Users/apple/Desktop/Create WS-ACO/MyCode')
from IaaSCloudWorkflowScheduler.Constants import Constants

internalId = 0

class VM:
    TYPE_NO = 10

    def __init__(self, type):
        global internalId
        self.type = type
        self.id = internalId
        internalId += 1
        self.LAUNCH_TIME = 0
        self.NETWORK_SPEED = Constants.BANDWIDTH

        self.SPEEDS = [1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.25, 0.2]
        self.MIPS = [100, 90, 80, 70, 60, 50, 40, 30, 25, 20]
        self.UNIT_COSTS = [20, 16.2, 12.8, 9.8, 7.2, 5, 3.2, 1.8, 1.25, 0.8]
        self.INTERVAL = 3600
        self.FASTEST = 0
        self.SLOWEST = 9



    def resetInternalId(self):
        global internalId
        internalId = 0
    
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

