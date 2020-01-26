class FileExtNotAllowed(Exception):

    def __init__(self, msg):
        super(FileExtNotAllowed, self).__init__(msg)