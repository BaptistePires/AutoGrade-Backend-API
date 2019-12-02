
class AssignmentNotValidError(BaseException):
    
    def __init__(self, msg, err):
        super(AssignmentNotValidError, self).__init__(msg, err)