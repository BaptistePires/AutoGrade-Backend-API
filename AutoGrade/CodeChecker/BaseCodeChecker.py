
class BaseCodeChecker():

    def __init__(self, assignment):
        super().__init__()
        self._assignment = assignment
        self._forbiddenImports = []

    def analyseCode(self) -> tuple:
        importsAndBuiltInt = True
        testIOs = True
        compile = None
        if self.getAssignment().isCompiled():
            compile = self._testCompile()
        importsAndBuiltInt = self._checkImportsAndBuiltIn()
        testIOs = self._runTestsIOs()
        
            
        return importsAndBuiltInt, testIOs, compile

    def _checkImportsAndBuiltIn(self) -> bool: return False

    def _runTestsIOs(self) -> bool: return False

    def _testCompile(self) -> bool: return False

    def getAssignment(self): return self._assignment