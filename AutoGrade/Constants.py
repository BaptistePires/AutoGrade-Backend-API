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
    }
    ,
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

##########
# Values #
##########

COMPILED_EXT = ['java']


########################
# Code Checkers values #
########################
PY_FORBIDDEN_IMPORTS = ['os','sys','__future__','_thread','_dummy_thread',
            'ctypes','dummy_threading','ftplib','importlib','logging','mailbox',
            'modulefinder','msilib','msvcrt','multiprocessing','nntplib','pipes','posix',
            'pwd','pty','runpy','sched','shutil','smtpd','smtplib','socket','socketserver',
            'spwd','ssl','subprocess','sysconfig','syslog','tabnanny','tarfile','telnetlib',
            'tempfile','termios','threading','tracemalloc','tty','time','turtle','urllib',
            'webbrowser','winreg','wsgiref','xml','zipapp','zipfile','zipimport','zlib']

# Allowed : bool, dict, enumerate, float, input, int, len, list, print, range, str, tuple, type
PY_FORBIDDEN_BUILT_IN = [
            'abs','all','any','ascii','breakpoint','bytearray','bytes','callable','chr',
            'classmethod','compile','complex','delattr','dir','divmod','eval','exec',
            'filter','format','frozenset','getattr','globals','hasattr','hash','hex','help',
            'id','isinstance','issubclass','iter','locals','max','map','memoryview','min',
            'next','object','oct','open','ord','pow','property','repr','reversed','set',
            'setattr','slice','sorted','staticmethod','sum','super','vars','zip','__import__',
        ]