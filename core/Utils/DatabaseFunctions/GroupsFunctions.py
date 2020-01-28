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


def getEvalGroupFromName(evalUserID: str, groupName: str) -> dict:
    collection = db.getCollection(GROUPS_DOCUMENT)
    print(evalUserID)
    group = collection.find_one({
        GROUPS_ID_EVAL_FIELD: ObjectId(evalUserID),
        GROUPS_NAME_FIELD: groupName})
    if group is None: raise GroupDoesNotExistException("")
    return group


def getAllGroupsFromUserId(userId: str) -> list:
    collection = db.getCollection(GROUPS_DOCUMENT)
    try:
        return [x for x in collection.find({GROUPS_ID_EVAL_FIELD: ObjectId(userId)})]
    except PyMongoError:
        raise ConnectDatabaseError('Error while getting group for the user with the id ' + userId)


def addAssignToGroup(groupId: str, assignId: str, deadline: datetime) -> None:
    collection = db.getCollection(GROUPS_DOCUMENT)
    assign = GROUPS_ASSIGNMENT_TEMPLATE
    assign[GROUPS_ASSIGNMENTS_IDS_FIELD] = ObjectId(assignId)
    assign[GROUPS_ASSIGNMENTS_DEADLINE] = deadline

    try:
        collection.find_one_and_update({'_id': ObjectId(groupId)}, {'$push': {
            GROUPS_ASSIGNMENTS_FIELD: assign.copy()
        }})
    except PyMongoError as e:
        raise ConnectDatabaseError('Error while adding an assignment to the group + ' + str(groupId) + ' : ' + str(e))


def addSubmissionToGroup(assignID: str, subID: str, groupID: str) -> None:
    collection = db.getCollection(GROUPS_DOCUMENT)
    try:
        r = collection.find_one_and_update({
            '_id': ObjectId(groupID),
            'assignments': {
                '$elemMatch': {
                    'assignments_ids': ObjectId(assignID)
                }
            }
        },
            {
                '$push': {
                    'assignments.$.submissions_ids': ObjectId(subID)
                }
            })
    except PyMongoError:
        raise ConnectDatabaseError('Error while adding submission to the group')
