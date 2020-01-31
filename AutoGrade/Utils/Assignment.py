from asyncore import file_dispatcher
from os import sep, path
from json import loads

"""
    La façon de stocker les fichiers retenue est pour l'instant : 
        - ASSIGNMENT FILE : xxx/id_user/assignment.ext
        - IOS FILE        : xxx/id_user/assignementios.json
        
    -> Si ce n'est pas garder, attention à bien modifier les chemins / !!!! \

"""


class Assignment(object):

    def __init__(self, filePath):
        self.__filePath = filePath
        self.__ext = ""
        self.__fileName = ""
        self.__ios = None
        self.__file = None
        self.__setFileNameAndExt()
        self.__setIos()
        self.loadFile()

    def __setIos(self):
        self.__ios = AssignmentIOs(self.getFileName() + "ios.json")

    def __setFileNameAndExt(self):
        file = self.__filePath.split(sep)
        file = file[len(file) - 1]
        self.__fileName = path.splitext(file)[0]
        self.__ext = path.splitext(file)[1].replace(".", "")

    def loadFile(self) -> None:
        self.__file = open(self.__filePath)


    def getFileName(self): return self.__fileName

    def getExt(self): return self.__ext

    def getIos(self): return self.__ios.getIos()


class AssignmentIOs(object):

    def __init__(self, filePath):
        self.__filePath = filePath
        self.__ios = []
        self.__load()


    def __load(self):
        with open(self.__filePath, "r") as f:
            self.__ios = loads(f.read())

    def getIos(self): return self.__ios

# a = Assignment("/test/test/test.py")
# print(a.getIos())
