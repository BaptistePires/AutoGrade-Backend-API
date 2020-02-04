from .BaseCodeChecker import BaseCodeChecker
from subprocess import Popen, PIPE, TimeoutExpired
from Constants import JAVA_COMPILER, JAVA_ALLOWED_IMPORTS, JAVA_CMD
from re import split
from os import sep, chdir, getcwd, mkdir
from shutil import copy

class JavaCodeChecker(BaseCodeChecker):
    """
        This class is the class used to check java code.
    """

    def __init__(self, assignment):
        super().__init__(assignment)

    def _testCompile(self) -> bool:
        """
            Method doc in mother class.
        """
        # currentDir = getcwd()

        compilingPath = self.getAssignment().getFolder() + sep
        process = Popen([JAVA_COMPILER, self.getAssignment().getOriginalFilename()], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        _, stdout = process.communicate()
        if len(stdout) > 0:
            return False
        else:
            return True




    def _checkImportsAndBuiltIn(self) -> bool:
        """
            Method doc in mother class.
                -> As it's always the first method to be
        """
        import os

        with open(self.getAssignment().getOriginalFilename(), 'r') as f:
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

        strFile = ""
        with open(self.getAssignment().getOriginalFilename(), 'r') as f:
            for line in f.readlines():
                strFile += line.replace('\n', '')

        mainfunct = re.search(
            '\s*static\s*void\s*main\s*\(\s*String\s*\[\]\s*[^\)]*\)', strFile, re.IGNORECASE)

        countOpen = 0
        countClose = 0 
        pos = -1
        for i, c in enumerate(strFile[int(mainfunct.end()) -1:]):
            print(c)
            if c == '{': 
                countOpen+=1
            if c == '}': 
                countOpen-=1
                if countOpen == 0:
                    pos = i
                    break 
        strFile = strFile[:mainfunct.end() + pos - 1] + 'import java.io.*;try{Process p = Runtime.getRuntime().exec(new String[]{"cp","/proc/self/statm","./statm"});}catch(IOException e){}' +strFile[int(mainfunct.end()) + pos -1 :]
        with open('Test_insert.java', 'w') as f:
            f.write(strFile)
        return True

    def _runTestsIOs(self) -> list:
        """
            Method doc in mother class.
        """

        successIOs = [0 for x in range(len(self.getAssignment().getIOs()))]

        compiledPath = self.getAssignment().getCompiledName()
        args = [JAVA_CMD, compiledPath]
        for i, io in enumerate(self._assignment.getIOs()):
            process = Popen(args, stdin=PIPE, stdout=PIPE)
            try:
                stdin, _ = process.communicate(bytes(io[0].encode(encoding='UTF-8')), timeout=15)
                print(stdin, _)
                if str(stdin.decode('UTF-8')).replace('\n', '') == str(io[1]):
                    successIOs[i] = 1
            except TimeoutExpired:
                print('err timeout')
                process.kill()
                continue

        return successIOs