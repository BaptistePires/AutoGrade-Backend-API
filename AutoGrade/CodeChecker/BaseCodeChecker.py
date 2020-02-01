from abc import ABCMeta, abstractmethod

class BaseCodeChecker():

    def __init__(self, assignment):
        super().__init__()
        self._assignment = assignment
        self._forbiddenImports = []

    def analyseCode(self) -> tuple:
        importsAndBuiltInt = True
        testIOs = True
        compile = None

        importsAndBuiltInt = self._checkImportsAndBuiltIn()
        testIOs = self._testIOs()
        if self._assignment.isCompiled():
            compile = self._testCompile()

        return importsAndBuiltInt, testIOs, compile

    def _checkImportsAndBuiltIn(self) -> bool:pass

    def _runTestsIOs(self) -> bool: pass

    def _testCompile(self) -> bool: pass
    def getAssignment(self): return self._assignment