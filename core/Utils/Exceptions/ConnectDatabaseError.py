class ConnectDatabaseError(BaseException):

    def __init__(self, msg):
        super(ConnectDatabaseError, self).__init__(msg)