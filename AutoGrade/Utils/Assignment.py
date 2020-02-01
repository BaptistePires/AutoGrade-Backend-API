from asyncore import file_dispatcher
from os import sep, path
from json import loads

from .DatabaseConstants import *

"""
    La façon de stocker les fichiers retenue est pour l'instant : 
        - ASSIGNMENT FILE : xxx/id_user/assignment.ext
        - IOS FILE        : xxx/id_user/assignementios.json
        
    -> Si ce n'est pas garder, attention à bien modifier les chemins / !!!! \

"""


class Assignment(object):

    def __init__(self, fullPath: str):
        super().__init__()
        self.__filePath = fullPath
        self.__ext = ""
        self.__fileName = ""
        self.__ios = []
        self.__file = None
        self.__setFileNameAndExt()

    @staticmethod
    def fromDBObject(dbAssignment: ASSIGNMENT_ITEM_TEMPLATE, assignmentFolder: str):
        assignment = Assignment(assignmentFolder + sep + dbAssignment[ASSIGNMENT_FILENAME])
        assignment.setIOs([io.split(':') for io in dbAssignment[ASSIGNMENT_INPUT_OUTPUTS]])
        assignment.loadFile()
        return assignment

    def setIOs(self, ios: list):
        self.__ios = ios

    def __setFileNameAndExt(self):
        file = self.__filePath.split(sep)
        file = file[len(file) - 1]
        self.__fileName = path.splitext(file)[0]
        self.__ext = path.splitext(file)[1].replace(".", "")

    def loadFile(self) -> None:
        self.__file = open(self.__filePath)

    def getFileName(self): return self.__fileName

    def getExt(self): return self.__ext

    def getIOs(self): return self.__ios

    def getFilePath(self): return self.__filePath

    def getFile(self): return self.__file
    
    def __str__(self) -> str:
        return 'Assignment path: {path}'.format(path=self.__filePath)
