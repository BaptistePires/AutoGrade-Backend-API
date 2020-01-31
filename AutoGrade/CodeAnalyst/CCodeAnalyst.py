from core.AutoGrade.CodeAnalyst.BaseCodeAnalyst import BaseCodeAnalyst

class CCodeAnalyst(BaseCodeAnalyst):

    def __init__(self, assignment):
        super(CCodeAnalyst, self).__init__(assignment=assignment)

    def analyseCode(self):
        pass