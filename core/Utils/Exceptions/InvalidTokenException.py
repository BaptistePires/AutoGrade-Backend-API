
class InvalidTokenException(BaseException):

    def __init__(self, msg, err):
        super(InvalidTokenException, self).__init__(msg, err)