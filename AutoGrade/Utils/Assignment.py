from asyncore import file_dispatcher
from os import sep, path
from json import loads
from Constants import COMPILED_EXT
from .DatabaseConstants import ASSIGNMENT_ITEM_TEMPLATE, ASSIGNMENT_FILENAME, ASSIGNMENT_INPUT_OUTPUTS, \
    CANDIDATE_ASSIGNMENT_SUBMISSION_TEMPLATE, ASSIGNMENT_ORIGINAL_FILENAME


class Assignment(object):
    """
        This class will be used to represent an assignment to be tested or a submission.
    """

    def __init__(self, fullPath: str, _id:str, originalFilenam:str):
        super().__init__()
        self.__filePath = fullPath
        self.__ext = ""
        self.__fileName = ""
        self.__ios = []
        self.__file = None
        self.__originalFilename = originalFilenam
        self.__id = str(_id)
        self.__setFileNameAndExt()

    @staticmethod
    def fromDBObject(dbAssignment: ASSIGNMENT_ITEM_TEMPLATE, assignmentFolder: str):
        """
            This method set up an Assignmetn object from an assignment in the database.
        :param dbAssignment: assignment from the database.
        :param assignmentFolder: Folder where the assignment file is located.
        :return: Assignment
        """
        assignment = Assignment(assignmentFolder + sep + dbAssignment[ASSIGNMENT_FILENAME], _id=dbAssignment['_id'], originalFilenam=dbAssignment[ASSIGNMENT_ORIGINAL_FILENAME])
        assignment.setIOs(
            [[io, dbAssignment[ASSIGNMENT_INPUT_OUTPUTS][io]] for io in dbAssignment[ASSIGNMENT_INPUT_OUTPUTS]])
        return assignment

    @staticmethod
    def formatForSubmissionCorrection(submission: CANDIDATE_ASSIGNMENT_SUBMISSION_TEMPLATE,
                                      dbAssignment: ASSIGNMENT_ITEM_TEMPLATE, folderPath: str):
        """
            This method set up a Assignment object from a submission database object.
        :param submission: Submission from the database.
        :param dbAssignment: Database assignment object.
        :param folderPath: Folder where the assignment file is located.
        :return: Assignment object
        """
        assignment = Assignment(folderPath + sep + submission[ASSIGNMENT_FILENAME], _id=submission['_id'], originalFilenam=submission[ASSIGNMENT_ORIGINAL_FILENAME])
        assignment.setIOs(
            [[io, dbAssignment[ASSIGNMENT_INPUT_OUTPUTS][io]] for io in dbAssignment[ASSIGNMENT_INPUT_OUTPUTS]])

        return assignment

    def setIOs(self, ios: list):
        self.__ios = ios

    def __setFileNameAndExt(self):
        """
            Method that sets up the file name and extension from the full path of the assignment
        :return:
        """
        file = self.__filePath.split(sep)
        file = file[len(file) - 1]
        self.__fileName = path.splitext(file)[0]
        self.__ext = path.splitext(file)[1].replace(".", "")

    def getFileName(self):
        return self.__fileName

    def getExt(self):
        return self.__ext

    def getIOs(self):
        return self.__ios

    def getFilePath(self):
        return self.__filePath

    def getFile(self):
        return self.__file

    def isCompiled(self) -> bool:
        return True if self.getExt() in COMPILED_EXT else False

    def getCompiledPath(self):

        if self.getExt() == 'java':
            return path.dirname(self.getFilePath()) + sep + 'Main'

    def getCompiledName(self):
        if self.getExt() == 'java':
            return self.getOriginalFilename().split('.')[0]
        else:
            return self.getOriginalFilename()
    def getFolder(self):

        return path.dirname(self.getFilePath())

    def getLaunchCommand(self):
        if self.getExt() == 'java':
            return 'java'
        else:
            return 'python3'

    def getExecutableFileName(self):
        if self.getExt() == 'py':
            return self.__fileName + '.' + 'py'
        else:
            return 'Main'

    def getID(self):return self.__id

    def getOriginalFilename(self): return self.__originalFilename

    def __str__(self) -> str:
        return 'Assignment path: {path}'.format(path=self.__filePath)
