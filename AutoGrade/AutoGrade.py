###########
# Imports #
###########
from Exceptions.AssignmentFileNotFoundError import AssignmentFileNotFoundError
from Exceptions.AssignmentIOsNotFoundError import AssignmentIOsNotFoundError
from Exceptions.WrongAsignmentLanguageError import WrongAsignmentLanguageError
from Exceptions.AssignmentNotValidError import AssignmentNotValidError
from Utils.Assignment import Assignment
from sys import argv
from Constants import COMMANDS, TOTAL_RUNS
from Utils.DatabaseHandlerSingleton import DatabaseHandlerSingleton as DB
from Utils.DatabaseConstants import *
from os import sep
from statistics import mean
from CodeChecker.JavaCodeChecker import JavaCodeChecker
from CodeChecker.PyCodeChecker import PyCodeChecker
from CodeAnalyst.CodeAnalyst import CodeAnalyst

class AutoGrade(object):

    def __init__(self, idAssignment: str=None, submissionID: str=None, isEval=None, idUser=None):
        super(AutoGrade, self).__init__()
        self.__idUser = idUser
        self.__idAssignment = idAssignment
        self.__isEval = isEval
        self.__idSub = submissionID

    def checkAssignment(self, params: dict) -> bool:
        assignmentFromDb = DB.getInstance().getAssignmentFromID(self.__idAssignment)
        assignment = Assignment.fromDBObject(dbAssignment=assignmentFromDb, assignmentFolder=params['assignment_folder_path'] + sep + self.__idAssignment )
        codeChecker = JavaCodeChecker(assignment) if assignment.getExt() == 'java' else PyCodeChecker(assignment)
        imports, ios, successCompile = codeChecker.analyseCode()
        isValid = all((imports, True if ios.count(1) == len(ios) else False , successCompile if assignment.isCompiled() else True))
        if not isValid:
            self.setEvaluatorStats(maxRSS=None, cpuTimes=None, isValid=isValid, fileSize=None,assignmentID=self.__idAssignment)
            return
        codeAnalyst = CodeAnalyst(assignment=assignment, successIOs=ios)
        analysisResult = codeAnalyst.analyse()
        self.setEvaluatorStats(maxRSS=analysisResult['maxRSS'], cpuTimes=analysisResult['cpuTimes'], isValid=isValid, fileSize=analysisResult['fileSize'], assignmentID=self.__idAssignment)
    
    def setEvaluatorStats(self, maxRSS:int, cpuTimes: list, isValid: bool, fileSize: int, assignmentID:str) -> None:
        if isValid:
            cpuTimeAvg = self.getValuesAvg(cpuTimes=cpuTimes)
            DB.getInstance().setAssignmentCheckResult(assignmentID=assignmentID, cpuTimeAvg=cpuTimeAvg, maxRSS=maxRSS, fileSize=fileSize)
        else:
            DB.getInstance().setAssignmentNotValid(assignmentID=self.__idAssignment)
            
    def correctSubmission(self, params: dict) -> None:
        submission = DB.getInstance().getSubmissionFromID(params['submissionID'])
        dbAssignment = DB.getInstance().getAssignmentFromID(submission[ASSIGNMENT_SUB_ASSIGN_ID])
        folderPath = params['assignment_folder_path'] + sep + str(submission[ASSIGNMENT_SUB_GROUP_ID]) + sep + str(dbAssignment['_id'])
        assignSub = Assignment.formatForSubmissionCorrection(submission=submission, dbAssignment=dbAssignment, folderPath=folderPath)
        codeChecker = JavaCodeChecker(assignSub) if assignSub.getExt() == 'java' else PyCodeChecker(assignSub)
        imports, ios, successCompile = codeChecker.analyseCode()
        isValid = all((imports, True if ios.count(1) > 0 else False, successCompile if assignSub.isCompiled() else True))
        if not isValid:
            self.setSubmissionStats(submission=submission)
            return 
        codeAnalyst = CodeAnalyst(assignment=assignSub, successIOs=ios)
        anylysisResult = codeAnalyst.analyse()
        successIOs = ios.count(1) / len(ios)
        self.setSubmissionStats(maxRSS=anylysisResult['maxRSS'], cpuTimes=anylysisResult['cpuTimes'], fileSize=anylysisResult['fileSize'], successIOs=successIOs, isValid=isValid, dbAssignment=dbAssignment, submission=submission)
    
    def setSubmissionStats(self,submission:dict, maxRSS: int=None, cpuTimes:list=None, fileSize:int=None, successIOs:float=None, isValid: bool=None, dbAssignment:dict=None) -> None:
        if not isValid:
            DB.getInstance().setSubmissionInvalid(submissionID=submission['_id'])
            return 
        
        cpuTimeAvg = self.getValuesAvg(cpuTimes)
        grade = self.getGradeForSubmission(maxRSS=maxRSS, cpuTimeAvg=cpuTimeAvg, fileSize=fileSize, dbAsignment=dbAssignment, successIOs=successIOs, submission=submission)

        DB.getInstance().setSubmissionsResults(grade=grade, maxRSS=maxRSS, cpuTimeStat=cpuTimeAvg, fileSize=fileSize, successIOs=successIOs, submissionID=submission['_id'])

    def getGradeForSubmission(self, maxRSS: float, cpuTimeAvg: float, fileSize: int, dbAsignment: dict, submission: dict, successIOs: float) -> float:
        grade = 0
        if maxRSS is not None and maxRSS > 0:
            memRatio = dbAsignment[ASSIGNMENT_STATISTICS_NAME][ASSIGNMENT_MEMORY_USED] / maxRSS
            if memRatio >= 0.7:
                grade += dbAsignment[ASSIGNMENT_MARKING_SCHEME_NAME][ASSIGNMENT_MEMORY_USED]
            else:
                grade += dbAsignment[ASSIGNMENT_MARKING_SCHEME_NAME][ASSIGNMENT_MEMORY_USED] * memRatio

        if cpuTimeAvg is not None and cpuTimeAvg > 0:
            cpuTimeRatio = dbAsignment[ASSIGNMENT_STATISTICS_NAME][ASSIGNMENT_STAT_TIME] / cpuTimeAvg
            if cpuTimeRatio >= 0.8:
                grade += dbAsignment[ASSIGNMENT_MARKING_SCHEME_NAME][ASSIGNMENT_STAT_TIME]
            else:
                grade += dbAsignment[ASSIGNMENT_MARKING_SCHEME_NAME][ASSIGNMENT_STAT_TIME] * cpuTimeRatio 

        if fileSize is not None and fileSize > 0:
            fileSizeRatio = dbAsignment[ASSIGNMENT_STATISTICS_NAME][ASSIGNMENT_FILE_SIZE] / fileSize
            if fileSizeRatio >= 0.9:
                grade += dbAsignment[ASSIGNMENT_MARKING_SCHEME_NAME][ASSIGNMENT_FILE_SIZE]
            else:
                grade += dbAsignment[ASSIGNMENT_MARKING_SCHEME_NAME][ASSIGNMENT_FILE_SIZE] * fileSizeRatio 
        
        return grade * successIOs

    def getValuesAvg(self, cpuTimes: list) -> tuple:
        cpuTimes = sorted(cpuTimes)
        # Filter times, remove lowest and highest
        cpuTimes = cpuTimes[int(TOTAL_RUNS *.40): int(TOTAL_RUNS*.60)]
        cpuTimeAvg = mean(cpuTimes)
        
        return cpuTimeAvg

    @staticmethod
    def check(params: dict):
        autoGrade = AutoGrade(idAssignment=params['idAssignment'])
        autoGrade.checkAssignment(params)

    @staticmethod
    def correct(params: dict) -> None:
        autoGrade = AutoGrade(submissionID=params['submissionID'])
        autoGrade.correctSubmission(params)


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
    print('gere')
    if len(argv) == 1:
        AutoGrade.help()
    elif len(argv) < 2:
        print('[AutoGrade - main] Missing arguments')
    else:
        cmd = argv[1]
        for c in COMMANDS:
            if cmd in COMMANDS[c]['cmd']:
                module = __import__('AutoGrade')
                _class = getattr(module, 'AutoGrade')
                try:
                    params = {p: argv[2 + i] for i, p in enumerate(COMMANDS[c]['params'])}
                    if len(params) > 0:
                        getattr(_class, COMMANDS[c]['func'])(params)
                    else:
                        getattr(_class, COMMANDS[c]['func'])()
                except ModuleNotFoundError as e:
                    print('[AuoGrade - main] Missing arguments')
                    break
                break