
class AssignmentFileNotFoundError(BaseException):
    
    def __init__(self, msg, err):
        super(AssignmentFileNotFoundError, self).__init__(msg, err)