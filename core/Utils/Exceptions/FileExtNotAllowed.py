class FileExtNotAllowed(BaseException):

    def __init__(self, msg):
        super(FileExtNotAllowed, self).__init__(msg)