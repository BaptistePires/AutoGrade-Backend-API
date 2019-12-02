###########
# Imports #
###########
from Exceptions.AssignmentFileNotFoundError import AssignmentFileNotFoundError
from Exceptions.AssignmentIOsNotFoundError import AssignmentIOsNotFoundError

class AutoGrade(object):

    def __init__(self, idUser=None, idAssignment=None):
        super(AutoGrade, self).__init__()
        self.__codeChecker = None
        self.__codeAnalyst = None
        self.__idUser = idUser
        self.__idAssignment = idAssignment
        self.__userAssignment = None

    def __loadData(self):
        try:
            # HERE FUNCTION TO LOAD USER ASSIGNMENT FILE #
            self.__loadUserAssignment()
            # ONCE BOTH DONE, INSTANTIATE CODE CHECKER AND CODE ANALYST #
        except AssignmentFileNotFoundError as e:

            print("[AutoGrade - __loadData]Exception] Exception -> ", e.__class__)

        except AssignmentIOsNotFoundError as e:
            print("[AutoGrade - __loadData]Exception] Exception -> ", e.__class__)


    def start(self):
        self.__loadData()

    def __loadUserAssignment(self) -> None:
        ## Load the assigmnt file and the IOS here. ##
        ## Raise expections when needed ##
        self.__userAssignment = None
        raise AssignmentFileNotFoundError("Test", None)



if __name__ == '__main__':
    ag = AutoGrade()
    ag.start()