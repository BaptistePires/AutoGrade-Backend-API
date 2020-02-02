################
# DB CONSTANTS #
################
USERS_DOCUMENT = "users"
EVALUATORS_DOCUMENT = "evaluators"
CANDIDATES_DOCUMENT = "candidates"
GROUPS_DOCUMENT = "groups"
ASSIGNMENTS_DOCUMENT = "assignments"
ASSIGNMENT_SUBMISSIONS_DOCUMENT = "assignments_sub"

############
# COMMANDS #
############

COMMANDS = {
    'correct': {
        'cmd': ['-c', '--correct'],
        'desc': 'Launch the correction program',
        'func': 'correct',
        'params': ['idAssignment'],
        'examples': [
            'python3 AutoGrade.py -c'
        ]
    },
    'check': {
        'cmd': ['-ch', '--check'],
        'func': 'check',
        'desc': 'Use this command to validate an evaluator assignment',
        'params': [
            'assignment_folder_path',
            'idAssignment'
        ],
        'examples': [
            'python3 AutoGrade.py --check 8e21scrserc2ser'
        ]
    },
    'help': {
        'cmd': ['-h', '--help'],
        'func': 'help',
        'desc': 'This command allows you to visualize the help panel',
        'params': [],
        'examples': [
            'python3 AutoGrade.py -h'
        ]
    }
}

############
# Sys cmds #
############
JAVA_COMPILER = 'javac'
JAVA_CMD = 'java'
PYTHON_CMD = 'python3'

##########
# Values #
##########

COMPILED_EXT = ['java']
MEM_VALUES = {
    'size': [],
    'resident': [],
    'shared': [],
    'text': [],
    'lib': [],
    'data': [],
    'dt': []
}
TOTAL_RUNS = 50

########################
# Code Checkers values #
########################
PY_FORBIDDEN_IMPORTS = ['os', 'sys', '__future__', '_thread', '_dummy_thread',
                        'ctypes', 'dummy_threading', 'ftplib', 'importlib', 'logging', 'mailbox',
                        'modulefinder', 'msilib', 'msvcrt', 'multiprocessing', 'nntplib', 'pipes', 'posix',
                        'pwd', 'pty', 'runpy', 'sched', 'shutil', 'smtpd', 'smtplib', 'socket', 'socketserver',
                        'spwd', 'ssl', 'subprocess', 'sysconfig', 'syslog', 'tabnanny', 'tarfile', 'telnetlib',
                        'tempfile', 'termios', 'threading', 'tracemalloc', 'tty', 'time', 'turtle', 'urllib',
                        'webbrowser', 'winreg', 'wsgiref', 'xml', 'zipapp', 'zipfile', 'zipimport', 'zlib']

# Allowed : bool, dict, enumerate, float, input, int, len, list, print, range, str, tuple, type
PY_FORBIDDEN_BUILT_IN = [
    'abs', 'all', 'any', 'ascii', 'breakpoint', 'bytearray', 'bytes', 'callable', 'chr',
    'classmethod', 'compile', 'complex', 'delattr', 'dir', 'divmod', 'eval', 'exec',
    'filter', 'format', 'frozenset', 'getattr', 'globals', 'hasattr', 'hash', 'hex', 'help',
    'id', 'isinstance', 'issubclass', 'iter', 'locals', 'max', 'map', 'memoryview', 'min',
    'next', 'object', 'oct', 'open', 'ord', 'pow', 'property', 'repr', 'reversed', 'set',
            'setattr', 'slice', 'sorted', 'staticmethod', 'sum', 'super', 'vars', 'zip', '__import__',
]

JAVA_FORBIDEN_IMPORTS = {
    'lang': [
        '*'
    ],
    'io': [
        '*'
    ],
    'util': [
        '*'
    ],
    'applet': [
        '*'
    ],
    'awt': [
        '*'
    ],
    'net': [
        '*'
    ],
    '*': [
        '*'
    ]
}

JAVA_ALLOWED_IMPORTS = {
    'lang': [

    ],
    'io': [],
    'util': [
        'Scanner'
    ],
    'applet': [],
    'awt': [],
    'net': [],
    '*': []
}
