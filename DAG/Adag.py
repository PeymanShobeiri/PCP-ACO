import sys
sys.path.append('/Users/apple/Desktop/Create WS-ACO/MyCode')

from DAG.PlainFilenameType import PlainFilenameType
from DAG.LinkageType import LinkageType
from DAG.StdioType import StdioType



class Adag:
    def __init__(self):
        self.__filenameList = []
        self.__jobList = []
        self.__childList = []
        self.__version = ''
        self.__name = ''
        self.__index = None
        self.__count = None
        self.__jobCount = ''
        self.__fileCount = None
        self.__childCount = None
    
    def getFilenameList(self):
        return self.__filenameList
    
    def setFilenameList(self, list):
        self.__filenameList = list

    def getJobList(self):
        return self.__jobList
    
    def setJobList(self, list):
        self.__jobList = list
    
    def getChildList(self):
        self.__childList
    
    def setChildList(self, list):
        self.__childList = list
    
    def getVersion(self):
        return self.__version
    
    def setVersion(self, version):
        self.__version = version

    def getName(self):
        return self.__name
    
    def setName(self, name):
        self.__name = name 
    
    def getIndex(self):
        return self.__index
    
    def setIndex(self, index):
        self.__index = index
    
    def getCount(self):
        return self.__count
    
    def setCount(self, count):
        self.__count = count
    
    def getJobCount(self):
        return self.__jobCount
    
    def setJobCount(self, jobCount):
        self.__jobCount = jobCount
    
    def getFileCount(self):
        return self.__fileCount
    
    def setFileCount(self, fileCount):
        self.__fileCount = fileCount
    
    def getChildCount(self):
        return self.__childCount
    
    def setChildCount(self, childCount):
        self.__childCount = childCount
    
    class Filename(PlainFilenameType):
        def __init__(self):
            self.__link = None
            self.__optional = None
    
        def  getLink(self):
            return self.__link
    
        def setLink(self, link):
            self.__link = link
    
        def getOptional(self):
            return self.__optional
    
        def setOptional(self, optional):
            self.__optional = optional
        
    
    class Job:
        def __init__(self):
            self.__argument= None
            self.__profileList = []
            self.__stdin = None
            self.__stdout = None
            self.__stderr = None
            self.__useList = []
            self.__namespace = ''
            self.__name = ''
            self.__version = ''
            self.__dvNamespace = ''
            self.__dvName = ''
            self.__dvVersion = ''
            self.__id = ''
            self.__runtime = ''
            self.__level = None
            self.__compound = ''

        def getArgument(self):
            return self.__argument
    
        def setArgument(self, argument):
            self.__argument = argument
    
        def getProfileList(self):
            return self.__profileList
    
        def setProfileList(self, list):
            self.__profileList = list
    
        def getStdin(self):
            return self.__stdin
    
        def setStdin(self, stdin):
            self.__stdin = stdin
    
        def getStdout(self):
            return self.__stdout
    
        def setStdout(self ,stdout ):
            self.__stdout = stdout
    
        def getStderr(self):
            return self.__stderr
    
        def setStderr(self, stderr):
            self.__stderr = stderr
    
        def getUseList(self):
            return self.__useList
    
        def setUseList(self, list):
            self.__useList =list
    
        def getNamespace(self):
            return self.__namespace
    
        def setNamespace(self, namespace):
            self.__namespace = namespace
    
        def getName(self):
            return self.__name
    
        def setName(self, name):
            self.__name = name
    
        def getVersion(self):
            return self.__version
    
        def setVersion(self, version):
            self.__version = version
    
        def getDvNamespace(self):
            return self.__dvNamespace
    
        def setDvNamespace(self, dvNamespace):
            self.__dvNamespace = dvNamespace
    
        def getDvName(self):
            return self.__dvName
    
        def setDvName(self, dvName):
            self.__dvName = dvName
    
        def getDvVersion(self):
            return self.__dvVersion
    
        def setDvVersion(self, dvVersion):
            self.__dvVersion = dvVersion
    
        def getId(self):
            return self.__id

        def setId(self, id):
            self.__id = id
    
        def getRuntime(self):
            return self.__runtime
    
        def setRuntime(self, runtime):
            self.__runtime = runtime
    
        def getLevel(self):
            return self.__level
    
        def setLevel(self, level):
            self.__level = level
    
        def getCompound(self):
            return self.__compound
    
        def setCompound(self, compound):
            self.__compound = compound

        class Argument:
            def __init__(self):
                self.__filenameList = []
    
            def getFilenameList(self):
                return self.__filenameList
    
            def setFilenameList(self,list):
                self.__filenameList = list
        
        class Profile:
            def __init__(self):
                self.__filenameList = []
                self.__key =''
                self.__namespace = None
                self.__origin =''
    
            def getFilenameList(self):
                return self.__filenameList
    
            def setFilenameList(self,list):
                self.__filenameList = list
    
            def getKey(self):
                return self.__key
    
            def setKey(self,key):
                self.__key = key
    
            def getNamespace(self):
                return self.__namespace
    
            def setNamespace(self, namespace):
                self.__namespace = namespace

            def getOrigin(self):
                return self.__origin
    
            def setOrigin(self, origin):
                self.__origin = origin

        class Stdin(StdioType):
            def __init__(self):
                self.__link = None
    
            def getLink(self):
                return self.__link
    
            def setLink(self, link):
                self.__link = link

        class Stdout(StdioType):
            def __init__(self):
                self.__link = None

            def getLink(self):
                return self.__link
    
            def setLink(self, link):
                self.__link = link

        class Stderr(StdioType):
            def __init__(self):
                self.__link = None

            def getLink(self):
                return self.__link
    
            def setLink(self, link):
                self.__link = link
    
    class Child:
        def __init__(self):
            self.__parentList = []
            self.__ref = None
    
        def getParentList(self):
            return self.__parentList
    
        def setParentList(self, list):
            self.__parentList = list
    
        def getRef(self):
            return self.__ref
    
        def setRef(self, ref):
            self.__ref = ref
        
        class Parent:
            def __init__(self):
                self.__ref = ''
    
            def getRef(self):
                return self.__ref
    
            def setRef(self, ref):
                self.__ref = ref


