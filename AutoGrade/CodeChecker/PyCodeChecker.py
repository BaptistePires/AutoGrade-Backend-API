from .BaseCodeChecker import BaseCodeChecker
from re import sub
class PyCodeChecker(BaseCodeChecker):
    
    def __init__(self, assignment):
        super().__init__(assignment)
        self._forbiddenImports = [
            'os',
            'sys',
            '__future__',
            '_thread',
            '_dummy_thread',
            'ctypes',
            'dummy_threading',
            'ftplib',
            'importlib',
            'logging',
            'mailbox',
            'modulefinder',
            'msilib',
            'msvcrt',
            'multiprocessing',
            'nntplib',
            'pipes',
            'posix',
            'pwd',
            'pty',
            'runpy',
            'sched',
            'shutil',
            'smtpd',
            'smtplib',
            'socket',
            'socketserver',
            'spwd',
            'ssl',
            'subprocess',
            'sysconfig',
            'syslog',
            'tabnanny',
            'tarfile',
            'telnetlib',
            'tempfile',
            'termios',
            'threading',
            'tracemalloc',
            'tty',
            'time',
            'turtle',
            'urllib',
            'webbrowser',
            'winreg',
            'wsgiref',
            'xml',
            'zipapp',
            'zipfile',
            'zipimport',
            'zlib'
        ]

        # Allowed : bool, dict, enumerate, float, input, int, len, list, print, range, str, tuple, type
        self.__builtInFuncForbidden = [
            'abs',
            'all',
            'any',
            'ascii',
            'breakpoint',
            'bytearray',
            'bytes',
            'callable',
            'chr',
            'classmethod',
            'compile',
            'complex',
            'delattr',
            'dir',
            'divmod',
            'eval',
            'exec',
            'filter',
            'format',
            'frozenset',
            'getattr',
            'globals',
            'hasattr',
            'hash',
            'hex',
            'help',
            'id',
            'isinstance',
            'issubclass',
            'iter',
            'locals',
            'max',
            'map',
            'memoryview',
            'min',
            'next',
            'object',
            'oct',
            'open',
            'ord',
            'pow',
            'property',
            'repr',
            'reversed',
            'set',
            'setattr',
            'slice',
            'sorted',
            'staticmethod',
            'sum',
            'super',
            'vars',
            'zip',
            '__import__',
        ]

   
    def _checkImportsAndBuiltIn(self) -> bool:
        with open(self.getAssignment().getFilePath(), 'r') as f:
            for line in f.readlines():
                words = line.split(' ')
                for w in words:
                    if 'import' in w:
                        if w in self._forbiddenImports:
                            return False
                    for f in self.__builtInFuncForbidden:
                        if f in w:        
                            # Need to check if it's not a variable with '_' inside its name
                            if sub('[^A-Za-z_]*', '', w) == f:
                                sub('[^A-Za-z_]*', '', w)
                                return False
        return True


    def _checkFunctionsCall(self) -> bool:
        print('PyCodeChecker - Not implemented yet')
        return True

    def getAssignment(self): return self._assignment
