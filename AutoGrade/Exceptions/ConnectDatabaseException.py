class ConnectDatabaseException(BaseException):
    def __init__(self, msg):
        super(ConnectDatabaseException, self).__init__(msg)