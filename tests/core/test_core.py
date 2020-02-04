import unittest
import datetime
import requests
import core.Utils.Utils as utils

class CoreTest(unittest.TestCase):
    def setUp(self):
        self.BASE_URL = 'http://127.0.0.1/'

    def testValidatePassword(self):
        self.assertFalse(utils.validatePassword(''))
        self.assertFalse(utils.validatePassword('password'))
        self.assertTrue(utils.validatePassword('Pass123#'))

    def testValidateEmail(self):
        self.assertFalse(utils.checkEmailFormat(''))
        self.assertFalse(utils.checkEmailFormat('email'))
        self.assertTrue(utils.checkEmailFormat('email@domain.fr'))

    def testIsTimestampBeforeNow(self):
        self.assertTrue(utils.isTimestampBeforeNow(datetime.datetime(2019, 3, 20, 22, 0, 0, 0).timestamp()))
        self.assertFalse(utils.isTimestampBeforeNow(datetime.datetime(2020, 2, 20, 22, 0, 0, 0).timestamp()))

    def testIsAccountValidated(self):
        self.assertFalse(utils.isAccountValidated("email@domain.com"))
        self.assertTrue(utils.isAccountValidated("quentin.joubert28@gmail.com"))

    def testIsAccountValidated(self):
        self.assertFalse(utils.isFileAllowed('test.java', ['py']))
        self.assertTrue(utils.isFileAllowed('test.py', ['py']))

if __name__ == '__main__':
    unittest.main()
