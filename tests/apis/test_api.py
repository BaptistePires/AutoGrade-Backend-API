import unittest
import requests
import core.Utils.Constants.DatabaseConstants as dbConst
import core.Utils.Constants.ApiModels as apiConst
import datetime

class ApiTest(unittest.TestCase):
    confirmToken = "";
    def setUp(self):
        self.BASE_URL = 'http://127.0.0.1:5000/'

    def test_01_AddEval(self):
        data = {
          dbConst.NAME_FIELD: "quentin",
          dbConst.LASTNAME_FIELD : "joubert",
          dbConst.PASSWORD_FIELD : "Password123#",
          dbConst.MAIL_FIELD : "quentin.joubert28@gmail.com",
          dbConst.ORGANISATION_FIELD : "org1"
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
          dbConst.MAIL_FIELD: "quentin.joubert28@gmail.com",
          dbConst.PASSWORD_FIELD : "Password123#"
        }
        r = requests.post(self.BASE_URL + "users/authenticate", json=data)
        print("testAuthentEval :" + r.text)
        self.token = r.json()['auth_token']
        self.assertEqual(r.status_code, requests.codes.ok)

    def test_04_OrderPremium(self):
        self.test_03_AuthentEval()
        option = {
            "X-API-KEY" : self.token
        }
        data = {
          "order_id" : "order1"
        }
        r = requests.post(self.BASE_URL + "users/evaluator/validate_premium", json=data, headers=option)
        print("testOrderPremium :" + r.text)
        self.assertEqual(r.status_code, requests.codes.ok)

    def test_04_AddGroup(self):
        self.test_03_AuthentEval()
        option = {
            "X-API-KEY" : self.token
        }
        data = {
          dbConst.GROUPS_NAME_FIELD : "group1"
        }
        r = requests.post(self.BASE_URL + "groups/create", json=data, headers=option)
        print("testAddGroup :" + r.text)
        self.idGroup = r.json()['groups_id']
        self.assertEqual(r.status_code, requests.codes.ok)

    def test_05_AddCandidate(self):
        self.test_03_AuthentEval()
        option = {
            "X-API-KEY" : self.token
        }
        data = {
          apiConst.CANDIDATE_MAIL : "quentin.joubert@etu.upmc.fr",
          apiConst.GROUP_NAME : "group1"
        }
        r = requests.post(self.BASE_URL + "users/evaluator/add/candidate", json=data,  headers=option)
        print("testAddCandidate :" + r.text)
        global confirmToken
        confirmToken = r.json()['confirm_token']
        self.assertEqual(r.status_code, requests.codes.ok)
      
    def test_06_ConfirmCandidate(self):
        data = {
          dbConst.NAME_FIELD: "quentin",
          dbConst.LASTNAME_FIELD : "joubert",
          dbConst.PASSWORD_FIELD : "Password123#",
          dbConst.MAIL_FIELD : "quentin.joubert@etu.upmc.fr",
          dbConst.ORGANISATION_FIELD : "org1"
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
        self.test_03_AuthentEval()
        option = {
            "X-API-KEY" : self.token
        }
        data = {
            dbConst.ASSIGNMENT_NAME : "assign1",
            dbConst.ASSIGNMENT_DESCRIPTION : "desc1",
            dbConst.ASSIGNMENT_INPUT_OUTPUTS : "8 12 : 20"
        }
        file = open('C:/Users/queom/Downloads/test.py','rb')
        files = [
            ('assignmentFile', file)
        ]
        marking_scheme_file_size="40"
        marking_scheme_cpu_time="30"
        marking_scheme_memory_used="20"
        r = requests.post(self.BASE_URL + "assignments/evaluator/create?marking_scheme_file_size=" + marking_scheme_file_size + "&marking_scheme_cpu_time=" + marking_scheme_cpu_time + "&marking_scheme_memory_used=" + marking_scheme_memory_used, data = data, files = files, headers=option)
        print("testAddAssign :" + r.text)
        self.idAssign = r.json()['assign_id']
        file.close()
        self.assertEqual(r.status_code, requests.codes.ok)

    def test_09_GroupAddAssign(self): 
        self.test_03_AuthentEval()
        self.test_09_AddAssign()
        option = {
            "X-API-KEY" : self.token
        }
        timestamp = datetime.datetime(2020, 2, 20, 22, 0, 0, 0).timestamp()
        data = {
            "group_name": "group1",
            "assignID": self.idAssign,
            "deadline": 1680747612.224927,
        }
        r = requests.put(self.BASE_URL + "groups/add/assignment", json=data, headers=option)
        print("testGroupAddAssign :" + r.text)
        self.assertEqual(r.status_code, requests.codes.ok)


    def test_10_GetAllAssign(self):
        self.test_03_AuthentEval()
        option = {
            "X-API-KEY" : self.token
        }
        r = requests.get(self.BASE_URL + "assignments/evaluator/get/all", headers=option)
        print("testGetAssign :" + r.text)
        self.assertEqual(r.status_code, requests.codes.ok)

    def test_11_AuthentCandidate(self):
        data = {
          dbConst.MAIL_FIELD: "quentin.joubert@etu.upmc.fr",
          dbConst.PASSWORD_FIELD : "Password123#"
        }
        r = requests.post(self.BASE_URL + "users/authenticate", json=data)
        print("testAuthentCandidate :" + r.text)
        self.token = r.json()['auth_token']
        self.assertEqual(r.status_code, requests.codes.ok)

    def test_12_AssignSubmit(self):
        self.test_09_GroupAddAssign()
        self.test_11_AuthentCandidate()
        self.test_13_GetCandidateGroup()
        option = {
            "X-API-KEY" : self.token
        }
        data = {
            "assignID": self.idAssign,
            "groupID": self.idGroup,
        }
        file = open('C:/Users/queom/Downloads/test.py','rb')
        files = [
            ('assignmentFile', file)
        ]
        r = requests.post(self.BASE_URL + "assignments/candidate/submit", data = data, files = files, headers=option)
        print("testAssignSubmit :" + r.text)
        file.close()
        self.assertEqual(r.status_code, requests.codes.ok)

    def test_13_GetCandidateGroup(self):
        self.test_11_AuthentCandidate()
        option = {
            "X-API-KEY" : self.token
        }
        r = requests.get(self.BASE_URL + "groups/get/candidate/all", headers=option)
        print("testGetCandidateGroup :" + r.text),
        self.idGroup = r.json()['groups'][0]['id']
        self.assertEqual(r.status_code, requests.codes.ok)

    def test_14_RemoveCandidate(self):
        self.test_03_AuthentEval()
        option = {
            "X-API-KEY" : self.token
        }
        r = requests.put(self.BASE_URL + "groups/evaluator/remove/candidate", headers=option)
        print("testRemoveCandidate :" + r.text),
        self.assertEqual(r.status_code, requests.codes.ok)

    def test_15_UpdateUser(self):
        self.test_03_AuthentEval()
        option = {
            "X-API-KEY" : self.token
        }
        data = {
          dbConst.NAME_FIELD: "quentin",
          dbConst.LASTNAME_FIELD : "joubert",
          dbConst.ORGANISATION_FIELD : "org1"
        }
        r = requests.put(self.BASE_URL + "/users/update", json=data, headers=option)
        print("testUpdateUser :" + r.text),
        self.assertEqual(r.status_code, requests.codes.ok)

    def test_16_DeleteUser(self):
        self.test_11_AuthentCandidate()
        option = {
            "X-API-KEY" : self.token
        }
        r = requests.delete(self.BASE_URL + "users/delete", headers=option)
        print("testDeleteUser :" + r.text),
        self.assertEqual(r.status_code, requests.codes.ok)

    def test_17_UpdateGroupName(self):
        self.test_03_AuthentEval()
        option = {
            "X-API-KEY" : self.token
        }
        data = {
          "group_id": "5e38186d548d886e47fd7863",
          "new_name": "group2"
        }
        r = requests.put(self.BASE_URL + "groups/update/name", json=data, headers=option)
        print("testUpdateGroupName :" + r.text),
        self.assertEqual(r.status_code, requests.codes.ok)

if __name__ == '__main__':
    unittest.main()
