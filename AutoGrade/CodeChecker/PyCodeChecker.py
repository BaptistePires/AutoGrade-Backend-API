from .BaseCodeChecker import BaseCodeChecker
from re import sub
from subprocess import Popen, PIPE, STDOUT, check_output, TimeoutExpired, CalledProcessError
from os import popen, kill, getpgid
from signal import SIGTERM
from Constants import PY_FORBIDDEN_IMPORTS, PY_FORBIDDEN_BUILT_IN, PYTHON_CMD


class PyCodeChecker(BaseCodeChecker):

    def __init__(self, assignment):
        super().__init__(assignment)
        self._forbiddenImports = PY_FORBIDDEN_IMPORTS
        self.__builtInFuncForbidden = PY_FORBIDDEN_BUILT_IN

    def _checkImportsAndBuiltIn(self) -> bool:
        """
            Method doc in mother class.
        """
        with open(self.getAssignment().getFilePath(), 'r') as f:
            for line in f.readlines():
                # TODO check ;
                words = line.split(' ')
                for w in words:
                    if 'import' in w:
                        if w in self._forbiddenImports:
                            return False
                    for f in self.__builtInFuncForbidden:
                        if f in w:
                            # Need to check if it's not a variable with '_' inside its name
                            if sub('[^A-Za-z_]*', '', w) == f:
                                return False
        return True

    def _runTestsIOs(self):
        """
            Method doc in mother class.
        """
        args = [PYTHON_CMD, self.getAssignment().getFilePath()]
        successIOs = [0 for x in range(len(self.getAssignment().getIOs()))]
        for i, io in enumerate(self._assignment.getIOs()):
            process = Popen(args, stdin=PIPE, stderr=PIPE, stdout=PIPE)
            try:
                stdin, _ = process.communicate(bytes(io[0].encode(encoding='UTF-8')), timeout=15)
                if str(stdin.decode('UTF-8')).replace('\n', '') == str(io[1]):
                    successIOs[i] = 1
            except TimeoutExpired:
                print('err timeout')
                process.kill()
                return successIOs

        return successIOs
