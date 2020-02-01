from .BaseCodeChecker import BaseCodeChecker
from re import sub
from subprocess import Popen, PIPE, STDOUT, check_output, TimeoutExpired, CalledProcessError
from os import popen, kill, getpgid
from signal import SIGTERM
from Constants import PY_FORBIDDEN_IMPORTS, PY_FORBIDDEN_BUILT_IN
class PyCodeChecker(BaseCodeChecker):
    
    def __init__(self, assignment):
        super().__init__(assignment)
        self._forbiddenImports =  PY_FORBIDDEN_IMPORTS
        self.__builtInFuncForbidden = PY_FORBIDDEN_BUILT_IN

   
    def _checkImportsAndBuiltIn(self) -> bool:
        with open(self.getAssignment().getFilePath(), 'r') as f:
            for line in f.readlines():
                words = line.split(' ')
                for w in words:
                    if 'import' in w:
                        if w in self._forbiddenImports:
                            print(w)
                            return False
                    for f in self.__builtInFuncForbidden:
                        if f in w:
                            # Need to check if it's not a variable with '_' inside its name
                            if sub('[^A-Za-z_]*', '', w) == f:
                                print(w)
                                return False
        return True


    def _runTestsIOs(self):
        args = ['python3', self.getAssignment().getFilePath()]
        for io in self._assignment.getIOs():
            process = Popen(args, stdin=PIPE, stderr=PIPE)
            try:
                process.communicate(bytes(io[0].encode(encoding='UTF-8')), timeout=5)
                if process.returncode != 0: return False
            except TimeoutExpired:
                print('err timeout')
                process.kill()
                return False
        return True
