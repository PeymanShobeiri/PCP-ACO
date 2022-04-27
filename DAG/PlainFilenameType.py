class PlainFilenameType:
    def __init__(self):
        self.__file = ''
    
    def getFile(self):
        return self.__file
    
    def setFile(self, file):
        self.__file = file