from enum import Enum

class LinkageType(Enum):
    NONE = "none"
    INPUT = "input"
    OUTPUT = "output"
    INOUT = "inout"

    def __init__(self, value):
        self.__value = value

    def xmlValue(self):
        return self.__value
    
    def convert(val):
        for inst in LinkageType.__members__.values():
            if inst.xmlValue() == val:
                return inst
        return None
