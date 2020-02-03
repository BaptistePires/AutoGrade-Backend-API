class AmountNotAllowed(BaseException):

    def __init__(self, msg):
        super(AmountNotAllowed, self).__init__(msg)