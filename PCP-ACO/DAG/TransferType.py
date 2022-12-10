from enum import Enum

class TransferType(Enum):
    FALSE = "false"
    OPTIONAL = "optional"
    TRUE = "true"
    
    def __init__(self, value):
        self.__value= value

    def xmlValue(self):
        return self.__value
    
    def convert(val):
        for inst in TransferType.__members__.values():
            if inst.xmlValue() == val:
                return inst
        return None
