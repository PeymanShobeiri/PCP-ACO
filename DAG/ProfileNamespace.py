from enum import Enum

class ProfileNamespace(Enum):
    PEGASUS = "pegasus"
    CONDOR = "condor"
    DAGMAN = "dagman"
    ENV = "env"
    HINTS = "hints"
    GLOBUS = "globus"
    SELECTOR = "selector"

    def __init__(self, value):
        self.__value= value

    def xmlValue(self):
        return self.__value
    
    def convert(val):
        for inst in ProfileNamespace.__members__.values():
            if inst.xmlValue() == val:
                return inst
        return None
