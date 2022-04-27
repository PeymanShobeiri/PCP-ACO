import sys
sys.path.append('/Users/apple/Desktop/Create WS-ACO/MyCode')
from DAG.PlainFilenameType import PlainFilenameType


class StdioType(PlainFilenameType):
    def __init__(self):
        self.__varname=''
    
    def getVarname(self):
        return self.__varname
    
    def setVarname(self, varname):
        self.__varname = varname
        