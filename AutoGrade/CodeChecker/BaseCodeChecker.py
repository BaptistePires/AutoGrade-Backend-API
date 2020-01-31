
class BaseCodeChecker(object):

    def __init__(self, assignment:'Assignment Object'):
        super(BaseCodeChecker, self).__init__()
        self.__assignment = assignment

    def analyseCode(self):pass

    def __checkImports(self):pass

    def __checkFunctionsCall(self): pass

    def getAssignment(self): return self.__assignment