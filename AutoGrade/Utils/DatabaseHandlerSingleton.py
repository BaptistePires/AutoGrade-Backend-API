from pymongo import MongoClient
from pymongo.errors import PyMongoError
from Exceptions.ConnectDatabaseException import ConnectDatabaseException
from Utils.DatabaseConstants import *
from bson import ObjectId


class DatabaseHandlerSingleton:
    DB_IP = '127.0.0.1'
    DB_PORT = 27017
    DB_NAME = 'AutoGrade-API'
    __INSTANCE = None

    def __init__(self):
        self.__ip = DatabaseHandlerSingleton.DB_IP
        self.__port = DatabaseHandlerSingleton.DB_PORT
        self.__client = None
        self.__db = None

    def connect(self):
        try:
            self.__client = MongoClient(host=self.__ip, port=self.__port)
            self.__db = self.__client.get_database(self.DB_NAME)
        except PyMongoError:
            raise ConnectDatabaseException(
                'Error while connection to the database')

    @staticmethod
    def getInstance():
        if DatabaseHandlerSingleton.__INSTANCE is None:
            DatabaseHandlerSingleton.__INSTANCE = DatabaseHandlerSingleton()
            DatabaseHandlerSingleton.__INSTANCE.connect()
            return DatabaseHandlerSingleton.__INSTANCE
        else:
            return DatabaseHandlerSingleton.__INSTANCE

    def __getCollection(self, collectionName):
        try:
            return self.__getDatabase()[collectionName]
        except PyMongoError as e:
            raise ConnectDatabaseException(
                '[ ' + self.__class__.__name__ + ' - __getCollection] Excecption : ' + str(e))
            # print('[ ' + self.__class__.__name__ + ' - __getCollection] Excecption : ' + str(e))

    def getAssignmentFromID(self, assignmentID: str) -> dict:
        collection = self.__getCollection(ASSIGNMENTS_DOCUMENT)
        try:
            return collection.find_one({
                '_id': ObjectId(assignmentID)
            })
        except PyMongoError as e:
            raise ConnectDatabaseException(
                '[ ' + self.__class__.__name__ + ' - getAssignmentFromID] Excecption : ' + str(e))

    def getEvaluatorFromID(self, evaluatorID: str) -> dict:
        collection = self.__getCollection(EVALUATORS_DOCUMENT)
        try:
            return collection.find_one({
                '_id': ObjectId(evaluatorID)
            })
        except PyMongoError as e:
            raise ConnectDatabaseException(
                '[ ' + self.__class__.__name__ + ' - getAssignmentFromID] Excecption : ' + str(e))

    def setAssignmentCheckResult(self, assignmentID: str, cpuTime: float, fileSize: int, virtualMem: int) -> None:
        collection = self.__getCollection(ASSIGNMENTS_DOCUMENT)
        try:
            return collection.find_one_and_update({
                '_id': ObjectId(assignmentID)
            },{
                '$set': {
                    ASSIGNMENT_STATISTICS_NAME: {
                        ASSIGNMENT_STAT_TIME: cpuTime,
                        ASSIGNMENT_FILE_SIZE: fileSize,
                        ASSIGNMENT_MEMORY_USED: virtualMem
                    },
                    ASSIGNMENT_IS_VALID: 0
                }
            })
        except PyMongoError as e:
            raise ConnectDatabaseException(
                '[ ' + self.__class__.__name__ + ' - getAssignmentFromID] Excecption : ' + str(e))
    
    def setAssignmentNotValid(self, assignmentID: str):
        collection =self.__getCollection(ASSIGNMENTS_DOCUMENT)
        try:
            return collection.find_one_and_update({
                '_id': ObjectId(assignmentID)
            },{
                '$set': {
                    ASSIGNMENT_IS_VALID: -1,
                }
            })
            

        except PyMongoError as e:
            raise ConnectDatabaseException(
                '[ ' + self.__class__.__name__ + ' - getAssignmentFromID] Excecption : ' + str(e))

    def getSubmissionFromID(self, submissionID: str) -> CANDIDATE_ASSIGNMENT_SUBMISSION_TEMPLATE:
        collection = self.__getCollection(ASSIGNMENT_SUBMISSIONS_DOCUMENT)
        try:
            return collection.find_one({
                '_id': ObjectId(submissionID)
            })
        except PyMongoError as e:
            raise ConnectDatabaseException(
                '[ ' + self.__class__.__name__ + ' - getAssignmentFromID] Excecption : ' + str(e))

    def setSubmissionInvalid(self, submissionID: str) -> None:
        collection = self.__getCollection(ASSIGNMENT_SUBMISSIONS_DOCUMENT)
        try:
            return collection.find_one_and_update({
                '_id': ObjectId(submissionID)
            }, {
                '$set': {
                    ASSIGNMENT_IS_VALID: -1,
                    ASSIGNMENT_SUB_GRADE: 0.0
                }
            })
        except PyMongoError as e:
            raise ConnectDatabaseException(
                '[ ' + self.__class__.__name__ + ' - getAssignmentFromID] Excecption : ' + str(e))

    def setSubmissionsResults(self, grade:float, maxRSS:int, cpuTimeStat:float, fileSize:int, successIOs:float, submissionID:str) -> None:
        collection = self.__getCollection(ASSIGNMENT_SUBMISSIONS_DOCUMENT)
        try:
            collection.find_one_and_update({
                '_id': ObjectId(submissionID)
            },{
                '$set': {
                    ASSIGNMENT_STATISTICS_NAME: {
                        ASSIGNMENT_STAT_TIME: cpuTimeStat,
                        ASSIGNMENT_FILE_SIZE: fileSize,
                        ASSIGNMENT_MEMORY_USED: maxRSS,
                        ASSIGNMENT_SUCCESS_IOS: successIOs
                    },
                    ASSIGNMENT_IS_VALID: 0,
                    ASSIGNMENT_SUB_GRADE:  grade
                }
            })

        except PyMongoError as e:
            raise ConnectDatabaseException(
                '[ ' + self.__class__.__name__ + ' - getAssignmentFromID] Excecption : ' + str(e))
    def __getClient(self):
        return self.__client

    def __getDatabase(self):
        return self.__db
