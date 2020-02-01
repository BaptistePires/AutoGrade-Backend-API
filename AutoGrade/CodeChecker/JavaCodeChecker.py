from .BaseCodeChecker import BaseCodeChecker
from subprocess import Popen, PIPE
from Constants import JAVA_COMPILER, JAVA_FORBIDEN_IMPORTS, JAVA_ALLOWED_IMPORTS, JAVA_CMD
from re import split
from os import system, sep, chdir, getcwd
from shutil import copy

class JavaCodeChecker(BaseCodeChecker):

    def __init__(self, assignment):
        super().__init__(assignment)
        self._forbiddenImports = JAVA_FORBIDEN_IMPORTS

    def _testCompile(self) -> bool:
        compilingPath = self.getAssignment().getFolder() + sep

        # copy(self.getAssignment().getFilePath(), compilingPath+'Main.java')
        # system('cp '+ self.getAssignment().getFilePath() + ' ' + compilingPath+ 'Main.java')

        # print(compilingPath + 'Main.java')
        process = Popen([JAVA_COMPILER, self.getAssignment().getFilePath()], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        _, stdout = process.communicate()
        if len(stdout) > 0:
            return False
        else:
            return True



    def _checkImportsAndBuiltIn(self) -> bool: 
        with open(self.getAssignment().getFilePath(), 'r') as f:
            for line in f.readlines():
                workingStr = line

                # As there are no extern package, they will all start with java.
                for javaImp in range(workingStr.count('java.'))   :

                    # Split the line with ';' or '.'
                    workingStr = split('[;.]+', workingStr)

                    # Get the next splited ''word'' and check which library is it 
                    package =workingStr[1].replace(' ', '')
                    if package in JAVA_ALLOWED_IMPORTS and package != '*':
                        allowedImports = JAVA_ALLOWED_IMPORTS[package]
                        subPackage = [s  for s in workingStr[2].split(' ') if len(s) > 0 and s.isalpha()][0]
                        if subPackage not in allowedImports: return False
                    else:
                        return False
        return True

    def _runTestsIOs(self) -> bool:
        successIOs = [0 for x in range(len(self.getAssignment().getIOs()))]
        currWorkingDir = getcwd()
        chdir(self.getAssignment().getFolder())
        args = [JAVA_CMD, self.getAssignment().getCompiledName()]
        for i, io in enumerate(self._assignment.getIOs()):
            process = Popen(args, stdin=PIPE, stdout=PIPE)
            try:
                stdin, _ = process.communicate(bytes(io[0].encode(encoding='UTF-8')), timeout=5)
                if process.returncode != 0:
                    chdir(currWorkingDir)
                    return successIOs

                if str(stdin.decode('UTF-8')) == str(io[1]):
                    successIOs[i] = 1
            except TimeoutExpired:
                print('err timeout')
                process.kill()
                chdir(currWorkingDir)
                return successIOs
        chdir(currWorkingDir)
        return successIOs