"""
    This file will contains all of the functions that need to call the database
    to retrieve groups data.
"""
from core.Utils.DatabaseHandler import DatabaseHandler
from core.Utils.Constants.DatabaseConstants import *
from bson import ObjectId
from core.Utils.Exceptions.GroupDoesNotExistException import GroupDoesNotExistException
from pymongo.errors import PyMongoError
from core.Utils.Exceptions.ConnectDatabaseError import ConnectDatabaseError
from datetime import datetime
db = DatabaseHandler()
db.connect()


def getEvalGroupFromName(eval: dict, groupName: str) -> dict:
    collection = db.getCollection(GROUPS_DOCUMENT)
    print(eval['_id'])
    group = collection.find_one({
        GROUPS_ID_EVAL_FIELD: ObjectId(eval['user_id']),
        GROUPS_NAME_FIELD: groupName})
    if group is None: raise GroupDoesNotExistException("")
    return group


def getAllGroupsFromUserId(userId: str) -> list:
    collection = db.getCollection(GROUPS_DOCUMENT)
    groups = []
    try:
        return [x for x in collection.find({GROUPS_ID_EVAL_FIELD: ObjectId(userId)})]
    except PyMongoError:
        raise ConnectDatabaseError('Error while getting group for the user with the id ' + userId)

def addAssignToGroup(groupId: str, assignId: str, deadline: datetime) -> None:
    collection = db.getCollection(GROUPS_DOCUMENT)
    try:
        collection.find_one_and_update({'_id': ObjectId(groupId)}, {'$push': {GROUPS_ASSIGNMENTS_FIELD: {
            GROUPS_ASSIGNMENTS_IDS_FIELD: ObjectId(assignId),
            GROUPS_ASSIGNMENTS_DEADLINE: deadline,
        }}})
    except PyMongoError:
        raise ConnectDatabaseError('Error while adding an assignment to the group + ' + groupId)