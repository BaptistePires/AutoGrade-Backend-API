import unittest
import requests
import core.Utils.Utils as utils

class ApiTest(unittest.TestCase):
    confirmToken = "";
    def setUp(self):
        self.BASE_URL = 'http://127.0.0.1:5000/'

    def test_01_AddEval(self):
        data = {
          "firstname": "quentin",
          "lastname": "joubert",
          "password": "QUENTIN123",
          "email": "quentin.joubert28@gmail.com",
          "organisation": "org1"
        }
        r = requests.post(self.BASE_URL + "users/evaluator/register", json=data)
        print("testAddEval" + r.text)
        global confirmToken
        confirmToken = r.json()["confirm_token"]
        self.assertEqual(r.status_code, requests.codes.ok)
        
    def test_02_ConfirmEval(self):
        r = requests.put(self.BASE_URL + "users/evaluator/confirmation/" + confirmToken)
        print("testConfirmEval" + r.text)
        self.assertEqual(r.status_code, requests.codes.ok)

    def test_03_AuthentEval(self):
        data = {
          "email": "quentin.joubert28@gmail.com",
          "password": "QUENTIN123"
        }
        r = requests.post(self.BASE_URL + "users/authenticate", json=data)
        print("testAuthentEval :" + r.text)
        self.token = r.json()['auth_token']
        self.assertEqual(r.status_code, requests.codes.ok)

    
    def test_04_AddGroup(self):
        self.test_03_AuthentEval()
        option = {
            "X-API-KEY" : self.token
        }
        data = {
          "name": "group1"
        }
        r = requests.post(self.BASE_URL + "groups/create", json=data, headers=option)
        print("testAddGroup :" + r.text)
        self.assertEqual(r.status_code, requests.codes.ok)

    def test_05_AddCandidate(self):
        self.test_03_AuthentEval()
        option = {
            "X-API-KEY" : self.token
        }
        data = {
          "mail_candidate": "quentin.joubert@etu.upmc.fr",
          "group_name": "group1"
        }
        r = requests.post(self.BASE_URL + "users/evaluator/add/candidate", json=data,  headers=option)
        print("testAddCandidate :" + r.text)
        global confirmToken
        confirmToken = r.json()['confirm_token']
        self.assertEqual(r.status_code, requests.codes.ok)
      
    def test_06_ConfirmCandidate(self):
        data = {
            "firstname": "quentin",
            "lastname": "joubert",
            "password": "QUENTIN123",
            "email": "quentin.joubert@etu.upmc.fr",
            "organisation": "org1"
        }
        r = requests.put(self.BASE_URL + "users/candidate/confirmation/" + confirmToken, json=data)
        print("testConfirmCandidate" + r.text)
        self.assertEqual(r.status_code, requests.codes.ok)

    def test_07_GetInfo(self):
        self.test_03_AuthentEval()
        option = {
            "X-API-KEY" : self.token
        }
        r = requests.get(self.BASE_URL + "users/get/info", headers=option)
        print("testGetInfo :" + r.text)
        self.assertEqual(r.status_code, requests.codes.ok)

    def test_08_GetGroupEval(self):
        self.test_03_AuthentEval()
        option = {
            "X-API-KEY" : self.token
        }
        r = requests.get(self.BASE_URL + "groups/get/evaluator/all", headers=option)
        print("testGetGroupEval :" + r.text)
        self.assertEqual(r.status_code, requests.codes.ok)

    def test_09_AddAssign(self):
        # TODO : Error
        self.test_03_AuthentEval()
        option = {
            "Content-Type" : "multipart/form-data",
            "X-API-KEY" : self.token
        }
        name="assign1"
        description="desc1"
        ios="8 12 : 20"
        data = {
            "mail_eval": "quentin.joubert28@gmail.com",
            "group_name": "group1",
            "assignID": "assign1",
            "deadline": "04/02/2020 00:00:00"
        }
        r = requests.post(self.BASE_URL + "assignments/evaluator/create", json=data, headers=option)
        print("testAddAssign :" + r.text)
        self.assertEqual(r.status_code, requests.codes.ok)

    def test_10_GetAllAssign(self):
        self.test_03_AuthentEval()
        option = {
            "X-API-KEY" : self.token
        }
        r = requests.post(self.BASE_URL + "assignments/evaluator/get/all", headers=option)
        print("testGetAssign :" + r.text)
        self.assertEqual(r.status_code, requests.codes.ok)

    def test_11_AuthentCandidate(self):
        data = {
          "email": "quentin.joubert@etu.upmc.fr",
          "password": "QUENTIN123"
        }
        r = requests.post(self.BASE_URL + "users/authenticate", json=data)
        print("testAuthentCandidate :" + r.text)
        self.token = r.json()['auth_token']
        self.assertEqual(r.status_code, requests.codes.ok)

    def test_12_AssignSubmit(self):
        # TODO : Error
        self.test_11_AuthentCandidate()
        option = {
            "Content-Type" : "multipart/form-data",
            "X-API-KEY" : self.token
        }
        data = {
            "assignID":"assign1",
            "groupID":"group1"
        }
        r = requests.put(self.BASE_URL + "assignments/candidate/submit", headers=option)
        print("testAssignSubmit :" + r.text)
        self.assertEqual(r.status_code, requests.codes.ok)

    def test_13_DeleteUser(self):
        # TODO : Error
        self.test_03_AuthentEval()
        option = {
            "X-API-KEY" : self.token
        }
        r = requests.delete(self.BASE_URL + "users/delete", headers=option)
        print("testDeleteUser :" + r.text),
        self.assertEqual(r.status_code, requests.codes.ok)

if __name__ == '__main__':
    unittest.main()