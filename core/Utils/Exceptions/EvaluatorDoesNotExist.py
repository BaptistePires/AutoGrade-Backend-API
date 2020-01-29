class EvaluatorDoesNotExist(BaseException):
    def __init__(self, msg):
        super(EvaluatorDoesNotExist, self).__init__(msg)