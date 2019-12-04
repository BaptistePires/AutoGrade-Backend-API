
class ExpiredTokenException(BaseException):

    def __init__(self, msg, err):
        super(ExpiredTokenException, self).__init__(msg, err)