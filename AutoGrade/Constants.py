COMMANDS = {
    'correct': {
        'cmd': ['-c', '--correct'],
        'desc': 'Launch the correction program',
        'func': 'correct',
        'params': [],
        'examples': [
            'python3 AutoGrade.py -c '
        ]
    }
    ,
    'check': {
        'cmd': ['-ch', '--check'],
        'func': 'check',
        'desc': 'Use this command to validate an evaluator assignment',
        'params': [
            'idAssignment',
            'idEvaluator'
        ],
        'examples': []
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
