
class CloudAcoResourceInstanceSet:

    def initialize(self, resources, count):
        id = 0
        coef = 1
        for j in range(resources.getSize()):
            resource = resources.getResource(j)
            tmp = {"instanceId": id, "resource": resource, "totalDuration": 0, "finishDuration": 0,
                   "processedTasksIds": set(), "currentStartTime": 0, "instanceFinishTime": 0.0, "totalCost": 0,
                   }
            id = coef * count
            coef += 1
            self.instances.append(tmp)

    def __init__(self, resources, count):

        self.instances = []
        self.initialize(resources, count)

    def getInstances(self):
        return self.instances

    def getInstanceByNum(self, index):
        if len(self.instances) > 0 and index < len(self.instances):
            return self.instances[index]

    def getFinishTime(self):
        max = -1
        for instances in self.instances.values():
            for instance in instances:
                if instance.getInstanceFinishTime() > max:
                    max = int(instance.getInstanceFinishTime())

        return max

    def resetPerAnt(self):
        for instance in self.instances:
            instance.reset()
