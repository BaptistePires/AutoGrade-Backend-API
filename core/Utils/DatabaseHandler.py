from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId
from core.Utils.Constants.DatabaseConstants import *
from core.Utils.Exceptions.ConnectDatabaseError import ConnectDatabaseError

class DatabaseHandler():

    def __init__(self):
        self.__ip = DB_IP
        self.__port = DB_PORT
        self.__connection = None
        self.__db = None

    def connect(self):
        try:
            self.__connection = MongoClient(host=self.__ip, port=self.__port, connectTimeoutMS=1000, socketTimeoutMS=1000)
            self.__db = self.__connection.get_database("AutoGrade-API")

        except Exception as e:
            print('Raise exc')
            raise ConnectDatabaseError('Error while connecting to the datase')

    def close(self):
        self.__db.logout()
        self.__connection.close()


    def insert(self, documentName, data):

        try:
            col = self.__db[documentName]
            id = col.insert_one(data)
            return id
        except PyMongoError:
            raise ConnectDatabaseError('Error while inserting data')

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
        try:
            col = self.getCollection("users")
            return [item[MAIL_FIELD] for item in col.find()]
        except PyMongoError:
            raise ConnectDatabaseError('Error while getting all users')

    def getOneUserByMail(self, email):
        try:
            col = self.getCollection('users')
            return col.find_one({MAIL_FIELD:email.lower()})
        except PyMongoError:
            raise ConnectDatabaseError('Error while getting the user')

    def updateConfirmationOfUserWithMail(self, email):
        try:
            col = self.getCollection("users")
            col.update_one({"email":email}, {'$set' :{"confirmed":'True'}})
        except PyMongoError:
            raise ConnectDatabaseError('Error while updating "confirmed" field.')

    def getUserMailById(self, id):
        try:
            col = self.getCollection(USERS_DOCUMENT)
            u = col.find_one({'_id': id})
            return u['email']
        except PyMongoError:
            raise ConnectDatabaseError('Error while getting user mail byt it\' id')

    def addGroupToUser(self, idUser, idGroup):
        try:
            col = self.getCollection(USERS_DOCUMENT)
            return col.update({'_id': idUser}, {'$push': {'groups': idGroup}})
        except PyMongoError:
            raise ConnectDatabaseError('Error while adding group to the user')


    ################################
    ### Groups Related functions ###
    ################################

    def getGroupByEvalIdAndName(self, id, name):
        try:
            col = self.getCollection(GROUPS_DOCUMENT)
            if col is None: return #TODO : handle return here
            return col.find_one({'name': name})
        except PyMongoError:
            raise ConnectDatabaseError('Error while getting group by it\'s name')

    def addUserToGroup(self, idGroup, idUser):
        try:
            col = self.getCollection(GROUPS_DOCUMENT)
            return col.update({'_id': idGroup}, {'$push': {'candidates_ids': idUser}})
        except PyMongoError:
            raise ConnectDatabaseError('Error while Adding user to the group')



if __name__ == "__main__":
    d = DatabaseHandler()
    d.connect()
    print(d.getAllUsersMail())
    # d.insert("err", {"test":"wesh alors"})

    d.close()