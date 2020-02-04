###########
# Imports #
###########
from Utils.Assignment import Assignment
from sys import argv
from Constants import COMMANDS, TOTAL_RUNS
from Utils.DatabaseHandlerSingleton import DatabaseHandlerSingleton as DB
from Utils.DatabaseConstants import *
from os import sep, chdir, mkdir, remove
from shutil import copy, rmtree
from statistics import mean
from CodeChecker.JavaCodeChecker import JavaCodeChecker
from CodeChecker.PyCodeChecker import PyCodeChecker
from CodeAnalyst.CodeAnalyst import CodeAnalyst
from Utils.DatabaseConstants import ASSIGNMENT_SUB_GROUP_ID, ASSIGNMENT_SUB_ASSIGN_ID

class AutoGrade(object):
    """
        This is the main class of the program that will check that an assignment works properly or will set
        the grade of a submission.
        To use this program, you can first call : python3 Autograde.py or python3 Autograde.py -h, this will show
        you all the commands available.
        The arguments used when you call this program are used to instantiate the correct function. It wont do a
        lot of check on the inputs you'll give to it, it'll assume that everything has already been checked up.
    """

    def __init__(self, idAssignment: str = None, submissionID: str = None, isEval=None, idUser=None):
        super(AutoGrade, self).__init__()
        self.__idUser = idUser
        self.__idAssignment = idAssignment
        self.__isEval = isEval
        self.__idSub = submissionID

    def checkAssignment(self, params: dict) -> None:
        """
            This function is used to check an evaluator that an evaluator created.
        :param params: Dict containing the parameters used when calling the program.
        :return: None.
        """
        assignmentFromDb = DB.getInstance().getAssignmentFromID(self.__idAssignment)
        assignment = Assignment.fromDBObject(dbAssignment=assignmentFromDb, assignmentFolder=params[
                                                                                                 'assignment_folder_path'] + sep + self.__idAssignment)

        # The purpose of that is to move to the right directory directly and works with files directly.
        # needed that because as we rename files when saving them, we can't compile java classes.
        chdir(params['assignment_folder_path'] + sep + params['idAssignment'])
        tmpFolder = assignment.getOriginalFilename().split('.')[0]
        mkdir(tmpFolder)
        copy(assignment.getFileName() + '.' + assignment.getExt(),
             tmpFolder + sep + assignment.getOriginalFilename())
        chdir(tmpFolder)
        codeChecker = JavaCodeChecker(assignment) if assignment.getExt() == 'java' else PyCodeChecker(assignment)
        imports, ios, successCompile = codeChecker.analyseCode()
        print(imports, ios, successCompile)
        isValid = all(
            (imports, True if ios.count(1) == len(ios) else False, successCompile if assignment.isCompiled() else True))
        if not isValid:
            self.setEvaluatorStats(maxRSS=None, cpuTimes=None, isValid=isValid, fileSize=None,
                                   assignmentID=self.__idAssignment)

        else:
            codeAnalyst = CodeAnalyst(assignment=assignment, successIOs=ios)
            analysisResult = codeAnalyst.analyse()
            print(analysisResult)
            self.setEvaluatorStats(maxRSS=analysisResult['maxRSS'], cpuTimes=analysisResult['cpuTimes'], isValid=isValid,
                                   fileSize=analysisResult['fileSize'], assignmentID=self.__idAssignment)
        chdir('./..')
        rmtree(tmpFolder)
    def setEvaluatorStats(self, assignmentID: str, maxRSS: int = None, cpuTimes: list = None, isValid: bool = None,
                          fileSize: int = None) -> None:
        """
            This method is used to set up the evaluator program's stats.
        :param assignmentID: Id of the assignment being tested.
        :param maxRSS: Maximum resident set size.
        :param cpuTimes: List of times expressed in seconds.
        :param isValid: Boolean, True if the program is valid, False otherwise.
        :param fileSize: File size in bytes.
        :return: None.
        """
        if isValid:
            cpuTimeAvg = self.getCpuTimeAvg(cpuTimes=cpuTimes)
            DB.getInstance().setAssignmentCheckResult(assignmentID=assignmentID, cpuTimeAvg=cpuTimeAvg, maxRSS=maxRSS,
                                                      fileSize=fileSize)
        else:
            print("here")
            DB.getInstance().setAssignmentNotValid(assignmentID=self.__idAssignment)

    def correctSubmission(self, params: dict) -> None:
        """
            This method is used to correct a candidate submission.
        :param params: Dict that contains paramater used to launch the program.
        :return: None.
        """
        submission = DB.getInstance().getSubmissionFromID(params['submissionID'])
        dbAssignment = DB.getInstance().getAssignmentFromID(submission[ASSIGNMENT_SUB_ASSIGN_ID])

        folderPath = params['assignment_folder_path'] + sep + str(submission[ASSIGNMENT_SUB_GROUP_ID]) + sep + str(
            dbAssignment['_id'])
        assignSub = Assignment.formatForSubmissionCorrection(submission=submission, dbAssignment=dbAssignment,
                                                             folderPath=folderPath)

        # The purpose of that is to move to the right directory directly and works with files directly.
        # needed that because as we rename files when saving them, we can't compile java classes.
        chdir(params['assignment_folder_path'] + sep + str(submission[ASSIGNMENT_SUB_GROUP_ID]) + sep + str(submission[ASSIGNMENT_SUB_ASSIGN_ID]))
        tmpFolder = assignSub.getOriginalFilename().split('.')[0]
        mkdir(tmpFolder)
        copy(assignSub.getFileName() + '.' + assignSub.getExt(),
             tmpFolder + sep + assignSub.getOriginalFilename())
        chdir(tmpFolder)

        codeChecker = JavaCodeChecker(assignSub) if assignSub.getExt() == 'java' else PyCodeChecker(assignSub)
        imports, ios, successCompile = codeChecker.analyseCode()

        isValid = all(
            (imports, True if ios.count(1) > 0 else False, successCompile if assignSub.isCompiled() else True))
        if not isValid:
            self.setSubmissionStats(submission=submission)
        else:
            codeAnalyst = CodeAnalyst(assignment=assignSub, successIOs=ios)
            anylysisResult = codeAnalyst.analyse()

            successIOs = ios.count(1) / len(ios)
            self.setSubmissionStats(maxRSS=anylysisResult['maxRSS'], cpuTimes=anylysisResult['cpuTimes'],
                                    fileSize=anylysisResult['fileSize'], successIOs=successIOs, isValid=isValid,
                                    dbAssignment=dbAssignment, submission=submission)
        chdir('./..')
        rmtree(tmpFolder)

    def setSubmissionStats(self, submission: dict, maxRSS: int = None, cpuTimes: list = None, fileSize: int = None,
                           successIOs: float = None, isValid: bool = None, dbAssignment: dict = None) -> None:
        """
            This method is used to set up the statistics of a submission program.
        :param submission: Assignment object.
        :param maxRSS: Maximum resident size.
        :param cpuTimes: List of time expressed in seconds.
        :param fileSize: Size of the file expressed in bytes.
        :param successIOs: Ratio that represents the success of the submissions program's for Inputs/Outputs provided.
        :param isValid: Boolean, True if the program is valid, False otherwise.
        :param dbAssignment: Database assignment used to retrieve marking scheme.
        :return: None.
        """
        if not isValid:
            DB.getInstance().setSubmissionInvalid(submissionID=submission['_id'])
            return

        cpuTimeAvg = self.getCpuTimeAvg(cpuTimes)
        grade = self.getGradeForSubmission(maxRSS=maxRSS, cpuTimeAvg=cpuTimeAvg, fileSize=fileSize,
                                           dbAsignment=dbAssignment, successIOs=successIOs, submission=submission)

        DB.getInstance().setSubmissionsResults(grade=grade, maxRSS=maxRSS, cpuTimeStat=cpuTimeAvg, fileSize=fileSize,
                                               successIOs=successIOs, submissionID=submission['_id'])

    def getGradeForSubmission(self, maxRSS: float, cpuTimeAvg: float, fileSize: int, dbAsignment: dict,
                              submission: dict, successIOs: float) -> float:
        """
            This method set up the grade for a submission program.
        :param maxRSS: Maximum resident size.
        :param cpuTimeAvg: Value of average time used by the submission program's.
        :param fileSize: File size in bytes.
        :param dbAsignment: Assignment related to the submission for the databse.
        :param submission: Assignment object that represents the submission.
        :param successIOs: Ratio that represents the success of the inputs or outputs for the program.
        :return: Float, the grade for the submission.
        """
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

    def getCpuTimeAvg(self, cpuTimes: list) -> float:
        """
            This method set the average of time sued by the program
        :param cpuTimes: list of times expressed in seconds,.
        :return: Float, the mean of time used by the program.
        """
        cpuTimes = sorted(cpuTimes)
        cpuTimes = cpuTimes[int(TOTAL_RUNS * .40): int(TOTAL_RUNS * .60)]
        cpuTimeAvg = mean(cpuTimes)
        return cpuTimeAvg

    @staticmethod
    def check(params: dict):
        """
            Method called when the program is called to check that the program of an assignment is working.
        :param params: Dict containing the arguments.
        :return: None.
        """
        autoGrade = AutoGrade(idAssignment=params['idAssignment'])
        autoGrade.checkAssignment(params)

    @staticmethod
    def correct(params: dict) -> None:
        autoGrade = AutoGrade(submissionID=params['submissionID'])
        autoGrade.correctSubmission(params)

    @staticmethod
    def help():
        """
            Method called when the help command is called.
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
