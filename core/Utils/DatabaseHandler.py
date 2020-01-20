from pymongo import MongoClient
from bson.objectid import ObjectId
from core.Utils.Constants.DatabaseConstants import *

class DatabaseHandler():

    def __init__(self):
        self.__ip = DB_IP
        self.__port = DB_PORT
        self.__connection = None
        self.__db = None

    def connect(self):
        try:
            self.__connection = MongoClient(host=self.__ip, port=self.__port)
            self.__db = self.__connection.get_database("AutoGrade-API")

        except Exception as e:
            print("Can't connect to the MongoDB database : ", e.args)

    def close(self):
        self.__db.logout()
        self.__connection.close()


    def insert(self, documentName, data):
        col = self.__db[documentName]
        id = col.insert_one(data)
        return id

    def getCollectionItems(self, collectionName):
        col = self.getCollection(collectionName)
        if col is not None:
            return [item for item in col.find()]

    def getCollectionItemsWithoutIFields(self, collectionName, noFields):
        col = self.getCollection(collectionName)
        if col is not None:
            return [item for item in col.find({},noFields)]


    def getCollection(self, colName):
        col = self.__db[colName]
        return col


    def emptyCol(self, colName):
        col = self.getCollection(colName)
        count = col.delete_many({})

    def findOneItemByColAndId(self, collectionName, id):
        # TODO : Handle param id type (Object id)
        col = self.getCollection('groups')
        item = col.find_one({'_id': id})
        return item

    def clearDocument(self, name):
        col = self.getCollection(name)
        col.delete_many({})

    ###############################
    ### Users Related functions ###
    ###############################

    def getAllUsers(self):
        col = self.getCollection("users")
        users = [item for item in col.find({}, {'_id':False})]
        return users

    def getAllUsersMail(self):
        col = self.getCollection("users")
        return [item["email"] for item in col.find()]

    def getOneUserByMail(self, email):
        col = self.getCollection('users')
        return col.find_one({"email":email})

    def updateConfirmationOfUserWithMail(self, email):
        col = self.getCollection("users")
        col.update_one({"email":email}, {'$set' :{"confirmed":'True'}})

    def getUserMailById(self, id):
        col = self.getCollection(USERS_DOCUMENT)
        u = col.find_one({'_id': id})
        return u['email']

    def addGroupToUser(self, idUser, idGroup):
        col = self.getCollection(USERS_DOCUMENT)
        return col.update({'_id': idUser}, {'$push': {'groups': idGroup}})


    ################################
    ### Groups Related functions ###
    ################################

    def getGroupByEvalIdAndName(self, id, name):
        col = self.getCollection(GROUPS_DOCUMENT)
        if col is None: return #TODO : handle return here
        return col.find_one({'name': name})

    def addUserToGroup(self, idGroup, idUser):
        col = self.getCollection(GROUPS_DOCUMENT)
        return col.update({'_id': idGroup}, {'$push': {'candidates_ids': idUser}})

    def getAllGroupsFromMail(self, mail):
        u = self.getOneUserByMail(mail)
        return [self.findOneItemByColAndId(i) for i in u['groups']]


if __name__ == "__main__":
    d = DatabaseHandler()
    d.connect()
    print(d.getAllUsersMail())
    # d.insert("err", {"test":"wesh alors"})

    d.close()