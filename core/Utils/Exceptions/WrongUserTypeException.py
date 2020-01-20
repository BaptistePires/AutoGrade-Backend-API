
class WrongUserTypeException(Exception):
    
    def __init__(self, msg):
        super(WrongUserTypeException, self).__init__(msg)