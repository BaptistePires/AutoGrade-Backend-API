from core.AutoGrade.CodeChecker.BaseCodeChecker import BaseCodeChecker

class PyCodeChecker(BaseCodeChecker):
    
    def __init__(self, assignment):
        super(PyCodeChecker, self).__init__(assignment=assignment)

    def analyseCode(self):pass # check what to do with this function

    def __checkImports(self) -> bool:
        with open(self.getAssignment().getFilepath(), 'r') as f:
            fContent = f.read()
            if "import" in fContent: return False
            else: return True

    def __checkExt(self): pass # Useless function as we test in Assignment class

    def __checkFunctionsCall(self): pass # Find out what to do with this function

    def getAssignment(self): return self.__assignment
