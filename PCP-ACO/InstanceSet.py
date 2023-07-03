import ResourceSet
import Instance


class InstanceSet:
    def __init__(self):
        self.__instances = []
        self.__size = 0

    def addInstance(self, inst):
        self.__instances.append(inst)
        self.__size += 1

    def removeInstance(self, inst):
        self.__instances.remove(inst)
        self.__size -= 1

    def getInstance(self, index):
        if index < self.__size:
            return self.__instances[index]
        else:
            return None

    def getSize(self):
        return self.__size
