###########
# Imports #
###########
from Exceptions.AssignmentFileNotFoundError import AssignmentFileNotFoundError
from Exceptions.AssignmentIOsNotFoundError import AssignmentIOsNotFoundError
from Exceptions.WrongAsignmentLanguageError import WrongAsignmentLanguageError
from Exceptions.AssignmentNotValidError import AssignmentNotValidError
from Utils import Assignment
from sys import argv
from Constants import COMMANDS


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
        try:
            self.__userAssignment = Assignment("/path/to/the/file/here")
        except FileNotFoundError:
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

    @staticmethod
    def help():
        """
            Help command for the program.
        """
        help = 'Here are the parameters allowed to call the programm :\n'
        for c in COMMANDS:
            help += '   {cmdName} : '.format(cmdName=c)
            for i, cmd in enumerate(COMMANDS[c]['cmd']):
                help += '{cmd}'.format(cmd=cmd)
                if i == len(COMMANDS[c]['cmd']) - 1:
                    help += '\n'
                else:
                    help += ', '
            help += '\n'
            help += '   description :\n'
            help += '       {desc}\n'.format(desc=COMMANDS[c]['desc'])
            help += '\n'
            help += '   examples:\n'
            for ex in COMMANDS[c]['examples']:
                help += '       {ex}\n'.format(ex=ex)

            help += '- - - - - - - - - - - - - - - - - - - - - - - - - - -\n'
        print(help)


if __name__ == '__main__':
    if len(argv) < 2:
        print('[AutoGrade - main] Missing arguments')
    else:
        cmd = argv[1]
        for c in COMMANDS:
            if cmd in COMMANDS[c]['cmd']:
                module = __import__('AutoGrade')
                cls = getattr(module, 'AutoGrade')
                getattr(cls, COMMANDS[c]['func'])()
        #
        # isEval = True
        # idUser = "erzrcdqcdsqcq"
        # idAssignment = "ecrzercr"
        # assignmentPath = "./assignmentEFSXV855.py"
        # ag = AutoGrade(isEval=True, idUser=idUser, idAssignment=idAssignment)
        # ag.start()
