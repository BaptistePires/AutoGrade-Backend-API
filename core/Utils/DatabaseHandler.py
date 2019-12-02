from pymongo import MongoClient
from bson.objectid import ObjectId

class DatabaseHandler():

    def __init__(self, ip, port):
        self.__ip = ip
        self.__port = port
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
        col = self.__getCollection(collectionName)
        if col is not None:
            return [item for item in col.find()]

    def getCollectionItemsWithoutIFields(self, collectionName, noFields):
        col = self.__getCollection(collectionName)
        if col is not None:
            return [item for item in col.find({},noFields)]


    def __getCollection(self, colName):
        col = self.__db[colName]
        return col


    def emptyCol(self, colName):
        col = self.__getCollection(colName)
        count = col.delete_many({})

    def findOneItemByColAndId(self, collectionName, id):
        # TODO : Handle param id type (Object id)
        col = self.__getCollection('groups')
        item = col.find_one(id)
        if item is not None:
            item['_id'] = str(item['_id'])
        else:
            # TODO : Throw exception Item not found
            pass

        return item


    ###############################
    ### Users Related functions ###
    ###############################

    def getAllUsers(self):
        col = self.__getCollection("users")
        users = [item for item in col.find({}, {'_id':False})]
        return users

    def getAllUsersMail(self):
        col = self.__getCollection("users")
        return [item["email"] for item in col.find()]


if __name__ == "__main__":
    d = DatabaseHandler("127.0.0.1", 27017)
    d.connect()
    d.insert("err", {"test":"wesh alors"})

    d.close()