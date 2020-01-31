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
            'assignment_folder_path'
            'idAssignment',
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
