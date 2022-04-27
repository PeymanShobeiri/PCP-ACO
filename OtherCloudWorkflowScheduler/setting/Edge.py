

from tkinter.messagebox import NO


class Edge:

    def __init__(self , source,destination) :
        self.__source = source
        self.__destination = destination
        self.__dataSize = None
    
    def getDataSize(self):
        return self.__dataSize
    
    def setDataSize(self , size):
        self.__dataSize = size
    
    def getSource(self):
        return self.__source
    
    def getDestination(self):
        return self.__destination
    
    def __str__(self):
        s = "Edge [source=" + self.__source + ", destination=" + self.__destination + ", size=" + self.__dataSize + "]"
        return s
    
    class EComparator:

        def __init__(self,isDestination,topoSort):
            self.isDestination = isDestination
            self.topoSort = topoSort
        
        def __gt__(self , other):
            task1 = None
            if self.isDestination :
                task1 = self.getDestination() 
            else:
                task1 = self.getSource()
            
            task2 = None
            if self.isDestination:
                task2 = other.getDestination()
            else:
                task2 = other.getSource
            
            index1 = self.topoSort[task1]
            index2 = self.topoSort[task2]

            if index1 > index2:
                return 1

            elif index1 < index2:
                return -1
            else:
                return 0
            