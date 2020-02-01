###########
# Imports #
###########
from Exceptions.AssignmentFileNotFoundError import AssignmentFileNotFoundError
from Exceptions.AssignmentIOsNotFoundError import AssignmentIOsNotFoundError
from Exceptions.WrongAsignmentLanguageError import WrongAsignmentLanguageError
from Exceptions.AssignmentNotValidError import AssignmentNotValidError
from Utils.Assignment import Assignment
from sys import argv
from Constants import COMMANDS
from Utils.DatabaseHandlerSingleton import DatabaseHandlerSingleton as DB
from Utils.DatabaseConstants import *
from os import sep

from CodeChecker.JavaCodeChecker import JavaCodeChecker
from CodeChecker.PyCodeChecker import PyCodeChecker


class AutoGrade(object):

    def __init__(self, idAssignment: str, isEval=None, idUser=None):
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
        elif self.__userAssignment.getExt() == 'java':
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

    def checkAssignment(self, params: dict) -> bool:
        assignmentFromDb = DB.getInstance().getAssignmentFromID(self.__idAssignment)
        #evaluator = DB.getInstance().getEvaluatorFromID(assignmentFromDb[ASSIGNMENT_AUTHOR_ID])
        assignment = Assignment.fromDBObject(dbAssignment=assignmentFromDb, assignmentFolder=params['assignment_folder_path'] + sep + self.__idAssignment )
        codeChecker = JavaCodeChecker(assignment) if assignment.getExt() == 'java' else PyCodeChecker(assignment)

        return codeChecker.analyseCode()

    @staticmethod
    def check(params: dict):
        autoGrade = AutoGrade(idAssignment=params['idAssignment'])
        isValid = autoGrade.checkAssignment(params)
        print(isValid)

if __name__ == '__main__':
    if len(argv) < 2:
        print('[AutoGrade - main] Missing arguments')
    else:
        cmd = argv[1]
        for c in COMMANDS:
            if cmd in COMMANDS[c]['cmd']:
                module = __import__('AutoGrade')
                cls = getattr(module, 'AutoGrade')
                try:
                    params = {p: argv[2 + i] for i, p in enumerate(COMMANDS[c]['params'])}
                    if len(params) > 0:
                        print(params)
                        getattr(cls, COMMANDS[c]['func'])(params)
                    else:
                        getattr(cls, COMMANDS[c]['func'])()
                except IndexError or KeyError:
                    print('[AuoGrade - main] Missing arguments')
                    break
                break