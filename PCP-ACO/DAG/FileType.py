from enum import Enum

class FileType(Enum):       
    DATA = "data"
    EXECUTABLE = "executable"
    PATTERN = "pattern"

    def __init__(self,value):
        self.__value = value
    
    def xmlValue(self):
        return self.__value

    def convert(val):
        for inst in FileType.__members__.values():
            if inst.xmlValue() == val:
                return inst
        return None

