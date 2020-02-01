from abc import ABCMeta, abstractmethod

class BaseCodeChecker():

    def __init__(self, assignment):
        super().__init__()
        self._assignment = assignment
        self._forbiddenImports = []

    def analyseCode(self) -> bool:
        if not self._checkImportsAndBuiltIn(): return False
        if not self._runTestsIOs(): return False
        return True     

    def _checkImportsAndBuiltIn(self) -> bool:pass

    def _runTestsIOs(self) -> bool:pass

    def getAssignment(self): return self._assignment