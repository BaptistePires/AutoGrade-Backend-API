
class GroupDoesNotExistException(BaseException):

    def __init__(self, msg):
        super(GroupDoesNotExistException, self).__init__(msg)