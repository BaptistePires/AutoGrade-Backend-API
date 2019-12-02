
class AssignmentIOsNotFoundError(BaseException):
    
    def __init__(self, msg, err):
        super(AssignmentIOsNotFoundError, self).__init__(msg, err)