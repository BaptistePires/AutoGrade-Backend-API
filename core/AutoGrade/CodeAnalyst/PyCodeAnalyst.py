from core.AutoGrade.CodeAnalyst.BaseCodeAnalyst import BaseCodeAnalyst

class PyCodeAnalyst(BaseCodeAnalyst):

    def __init__(self, assignment):
        super(PyCodeAnalyst, self).__init__(assignment=assignment)

    def analyseCode(self):
        pass

    def retrieveStats(self) -> None:
        cmd = "" # Build cmd to call the C subprogram to retrieve stats from the assignment

