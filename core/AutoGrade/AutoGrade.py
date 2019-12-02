###########
# Imports #
###########
from core.AutoGrade.Exceptions.AssignmentFileNotFoundError import AssignmentFileNotFoundError
from core.AutoGrade.Exceptions.AssignmentIOsNotFoundError import AssignmentIOsNotFoundError
from core.AutoGrade.Exceptions.WrongAsignmentLanguageError import WrongAsignmentLanguageError
from core.AutoGrade.Exceptions.AssignmentNotValidError import AssignmentNotValidError


class AutoGrade(object):

    def __init__(self, isEval, idUser, idAssignment):
        super(AutoGrade, self).__init__()
        self.__codeChecker = None
        self.__codeAnalyst = None
        self.__idUser = idUser
        self.__idAssignment = idAssignment
        self.__userAssignment = None
        self.__isEval = isEval

    def __setUp(self):
        try:
            # HERE FUNCTION TO LOAD USER ASSIGNMENT FILE #
            self.__loadUserAssignment()
            # ONCE BOTH DONE, INSTANTIATE CODE CHECKER AND CODE ANALYST #
        except AssignmentFileNotFoundError as e:
            print("[AutoGrade - __loadData] Exception -> ", e.args)
        except AssignmentIOsNotFoundError as e:
            print("[AutoGrade - __loadData] Exception -> ", e.args)

        # If the files were loaded successfully create the objects of the program.
        try:
            self.__loadCheckerAnalyst()
        except WrongAsignmentLanguageError as e:
            print("[AutoGrade - __loadData] Exception - > ", e.args)


    def start(self):
        self.__setUp()
        try:
            self.__codeChecker.checkCode()
        except AssignmentNotValidError as e:
            print("[AutoGrade - __start] Exception -> ", e.args)

    def __loadUserAssignment(self) -> None:
        ## Load the assigmnt file and the IO here. ##
        ## Raise expections when needed ##
        self.__userAssignment = None
        raise AssignmentFileNotFoundError("Test", None)

    def __loadCheckerAnalyst(self) -> None:
        if self.__userAssignment.getExt() == "py":
            # Create python code checker and analyst #
            pass
        elif self.__userAssignment.getExt() == "c":
            # Create C code checker and analyst #
            pass
        else:
            raise WrongAsignmentLanguageError("Le langage du fichier n'est pas pris en charge pas l'application", None)


if __name__ == '__main__':
    idUser = "erzrcdqcdsqcq"
    idAssignment = "ecrzercr"
    ag = AutoGrade(isEval=True, idUser=idUser, idAssignment=idAssignment)
    ag.start()