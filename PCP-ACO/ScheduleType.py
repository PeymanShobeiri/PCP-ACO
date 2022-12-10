from enum import Enum

class ScheduleType(Enum):
    Fastest = "Fastest"
    Cheapest = "Cheapest"
    IC_PCP = "IC-PCP"
    IC_PCPD2 = "IC-PCPD2"
    List = "List"
    IC_PCP2 = "IC-PCP2"
    IC_PCPD2_2 = "IC-PCPD2-2"
    List2 = "List2"
    IC_Loss = "IC_Loss"

    def __init__(self,value):
        self.__value = value
    
    def toString(self):
        return self.value
    
    def convert(self, val):
        for inst in ScheduleType.__members__.values():
            if inst.toString() == val:
                return inst
        
        return None