
class GroupDoesNotExistException(Exception):

    def __init__(self, msg):
        super(GroupDoesNotExistException, self).__init__(msg)