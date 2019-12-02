
class BaseCodeChecker(object):

    def __init__(self, code:'Code Object'):
        super(BaseCodeChecker, self).__init__()
        self.__code = code

    def analyseCode(self):pass

    def __checkImports(self):pass

    def __checkExt(self):pass

    def __checkFunctionsCall(self):pass