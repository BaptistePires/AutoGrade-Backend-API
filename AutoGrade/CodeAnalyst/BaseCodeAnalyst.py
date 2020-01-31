
class BaseCodeAnalyst(object):

    def __init__(self, assignment):
        super(BaseCodeAnalyst, self).__init__()
        self.__assignment = assignment

    def analyseCode(self):pass

    def getAssignment(self): return self.__assignment