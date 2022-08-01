import sys

sys.path.append('/Users/apple/Desktop/Create WS-ACO/MyCode')
from IaaSCloudWorkflowScheduler.ACO.CloudAcoResourceInstance import CloudAcoResourceInstance

import warnings


class CloudAcoResourceInstanceSet:
    # instances = {}
    # count = None

    def initialize(self, resources):
        id = 0
        for j in range(resources.getSize()):
            resource = resources.getResource(j)
            instances = []
            for i in range(self.count):
                instances.append(CloudAcoResourceInstance(resource, id))
                id += 1
            self.instances[resource] = instances

    def __init__(self, resources, count):
        self.count = count
        self.instances = {}
        self.initialize(resources)

    def getInstances(self):
        return self.instances

    def getCount(self):
        return self.count

    warnings.filterwarnings("ignore")

    def getFinishTime(self):  # Atomic  ?? what the ....
        max = -1
        for instances in self.instances.values():
            for instance in instances:
                if instance.getInstanceFinishTime() > max:
                    max = int(instance.getInstanceFinishTime())

        return max

    def resetPerAnt(self):
        for instances in self.instances.values():
            for instance in instances:
                instance.reset()
