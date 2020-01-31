from .BaseCodeChecker import BaseCodeChecker

class JavaCodeChecker(BaseCodeChecker):

    def __init__(self, assignment):
        super(JavaCodeChecker, self).__init__(assignment)

    def _checkImportsAndBuiltIn(self) -> bool: 
        print('not implemented yet')

    def _checkFunctionsCall(self) -> bool: 
        print('Not implemented yet')
