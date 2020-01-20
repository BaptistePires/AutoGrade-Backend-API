
class UserNotFoundException(Exception):
    
    def __init__(self, msg):
        super(UserNotFoundException, self).__init__(msg)