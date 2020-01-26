class WrongIOsFormat(BaseException):

    def __init__(self, msg):
        super(WrongIOsFormat, self).__init__(msg)