from core.AutoGrade.CodeChecker.BaseCodeChecker import BaseCodeChecker

class PyCodeChecker(BaseCodeChecker):
    
    def __init__(self, assignment):
        super(PyCodeChecker, self).__init__(assignment=assignment)

    def analyseCode(self):pass

    def __checkImports(self):pass

    def __checkExt(self):pass

    def __checkFunctionsCall(self): pass

    def getAssignment(self): return self.__assignment
