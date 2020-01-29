import unittest
import requests


class UserTest(unittest.TestCase):
    def setUp(self):
        self.BASE_URL = 'http://127.0.0.1:5000/'
        self.token = "";
        self.confirmToken = "";

    def testAAddEval(self):
        data = {
          "name": "quentin",
          "lastname": "joubert",
          "email": "quentin.joubert28@gmail.com",
          "password": "QUENTIN123",
          "organisation": "org1"
        }
        r = requests.post(self.BASE_URL + "users/evalualor/register", json=data)
        self.confirmToken = r.json()["confirm_token"]
        print("testAddEval" + r.text)
        self.assertEqual(r.status_code, requests.codes.ok)
        
    def testBConfirmEval(self):
        r = requests.put(self.BASE_URL + "users/evalualor/confirmation/" + self.confirmToken)
        print("testConfirmEval" + r.text)
        self.assertEqual(r.status_code, requests.codes.ok)

    def testCAuthentEval(self):
        data = {
          "email": "quentin.joubert28@gmail.com",
          "password": "QUENTIN123"
        }
        r = requests.post(self.BASE_URL + "users/authenticate", json=data)
        self.token = r.json()['auth_token']
        print("testAuthentEval :" + r.text)
        self.assertEqual(r.status_code, requests.codes.ok)

    
    def testDAddGroup(self):
        self.testCAuthentEval()
        option = {
            "X-API-KEY" : self.token
        }
        data = {
          "mail_eval": "quentin.joubert28@gmail.com",
          "name": "group1"
        }
        r = requests.post(self.BASE_URL + "groups/create", json=data, headers=option)
        print("testAddGroup :" + r.text)
        self.assertEqual(r.status_code, requests.codes.ok)

    def testEAddCandidate(self):
        self.testCAuthentEval()
        option = {
            "X-API-KEY" : self.token
        }
        data = {
          "mail_candidate": "quentin.joubert@etu.upmc.fr",
          "group_name": "group1"
        }
        r = requests.post(self.BASE_URL + "users/evaluator/add/candidate", json=data,  headers=option)
        self.confirmToken = r.json()["confirm_token"]
        print("testAddCandidate :" + r.text)
        self.assertEqual(r.status_code, requests.codes.ok)
      
    def testFConfirmCandidate(self):
        data = {
            "name": "quentin",
            "lastname": "joubert",
            "password": "QUENTIN123",
            "email": "quentin.joubert@etu.upmc.fr",
            "organisation": "org1"
        }

        r = requests.put(self.BASE_URL + "users/candidate/confirmation/" + self.confirmToken, json=data)
        print("testConfirmCandidate" + r.text)
        self.assertEqual(r.status_code, requests.codes.ok)

    def testGGetInfo(self):
        self.testCAuthentEval()
        option = {
            "X-API-KEY" : self.token
        }
        r = requests.get(self.BASE_URL + "users/get/info", headers=option)
        print("testGetInfo :" + r.text)
        self.assertEqual(r.status_code, requests.codes.ok)

    def testHGetGroupByMail(self):
        # TODO : Error 500
        self.testCAuthentEval()
        option = {
            "X-API-KEY" : self.token
        }
        mail = "quentin.joubert28@gmail.com"
        r = requests.post(self.BASE_URL + "groups/Get/AllByMail/" + mail, headers=option)
        print("testGetGroupByMail :" + r.text)
        self.assertEqual(r.status_code, requests.codes.ok)

    def testHGetGroup(self):
        # TODO : Error 500
        self.testCAuthentEval()
        option = {
            "X-API-KEY" : self.token
        }
        name = "group1"
        r = requests.get(self.BASE_URL + "groups/get/" + name, headers=option)
        print("testGetGroup :" + r.text),
        self.assertEqual(r.status_code, requests.codes.ok)

    def testIDeleteUser(self):
        self.testCAuthentEval()
        option = {
            "X-API-KEY" : self.token
        }
        r = requests.delete(self.BASE_URL + "users/delete", headers=option)
        print("testDeleteUser :" + r.text),
        self.assertEqual(r.status_code, requests.codes.ok)

if __name__ == '__main__':
    unittest.main()