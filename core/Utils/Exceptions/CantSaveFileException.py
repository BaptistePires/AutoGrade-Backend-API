class CantSaveFileException(BaseException):
    def __init__(self, msg):
        super(CantSaveFileException, self).__init__(msg)