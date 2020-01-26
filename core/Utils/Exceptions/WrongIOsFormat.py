class WrongIOsFormat(Exception):

    def __init__(self, msg):
        super(WrongIOsFormat, self).__init__(msg)