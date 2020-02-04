
class BaseCodeChecker():
    """
        This class is the base of coe checkers as the program needs to behave differently depending
        of the language.
        The 'template' design pattern will be used.
    """
    def __init__(self, assignment):
        super().__init__()
        self._assignment = assignment
        self._forbiddenImports = []

    def analyseCode(self) -> tuple:
        """
            This is the template method, the child classes have to override only _testCompile, _checkImportsAndBuiltIn
            and _runTestIos
        :return:
        """
        compile = True
        importsAndBuiltInt = self._checkImportsAndBuiltIn()
        print(importsAndBuiltInt, ' ?????')
        if self.getAssignment().isCompiled() and importsAndBuiltInt:
            compile = self._testCompile()

        testIOs = []
        if importsAndBuiltInt and compile:
            testIOs = self._runTestsIOs()

        return importsAndBuiltInt, testIOs, compile

    def _checkImportsAndBuiltIn(self) -> bool:
        """
        This method is used to check all the imports and the call of language built in methods
        :return: True if the program does not use forbidden libraries.
        """
        return False

    def _runTestsIOs(self) -> list:
        """
            This method is used to test all the Inputs/Outputs provided. It returns a list were the length
            is equals to the number of I/Os and each indexes is 1 if the I/O succeeded otherwise it's 0.
        :return: list
        """
        pass

    def _testCompile(self) -> bool:
        """
            This method is used to test if a program compiles.
        :return:
        """
        return False

    def getAssignment(self): return self._assignment
