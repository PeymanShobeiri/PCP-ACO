from .PlainFilenameType import PlainFilenameType
from .LinkageType import LinkageType
#from .FilenameType import FileType
#from .TransferType import TransferType


class FilenameType(PlainFilenameType):
    def __init__(self):
        super().__init__()
        self.__temporaryHint = ''
        self.__link = None
        self.__optional = None
        self.__register = None
        self.__transfer = None
        self.__type = None
        self.__size = ''

    def getTemporaryHint(self):
        return self.__temporaryHint
    
    def setTemporaryHint(self, temporaryHint):
        self.__temporaryHint = temporaryHint
    
    def getLink(self):
        return self.__link
    
    def setLink(self, link):
        self.__link = link
    
    def getOptional(self):
        return self.__optional
    
    def setOptional(self, optional):
        self.__optional = optional
    
    def getRegister(self):
        return self.__register
    
    def setRegister(self, register):
        self.__register = register
    
    def getTransfer(self):
        return self.__transfer

    def setTransfer(self, transfer):
        self.__transfer = transfer
    
    def getType(self):
        return self.__type
    
    def setType(self, type):
        self.__type = type
    
    def getSize(self):
        return self.__size
    
    def setSize(self, size):
        self.__size = size