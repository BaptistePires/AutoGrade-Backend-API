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
from core.Utils.DatabaseFunctions.AssignmentsFunctions import getSubmissionFromID
from core.Utils.DatabaseFunctions.UsersFunctions import *
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


def addAssignToGroup(groupId: str, assignId: str, deadline: float) -> None:
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


def addSubmissionToGroup(assignID: str, subID: str, groupID: str) -> bool:
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

        return r is not None
    except PyMongoError:
        raise ConnectDatabaseError('Error while adding submission to the group')



def getGroupNameFromId(groupID: str) -> str:
    collection = db.getCollection(GROUPS_DOCUMENT)
    try:
        group = collection.find_one({'_id': ObjectId(groupID)})
        if group is not None:
            return group[GROUPS_NAME_FIELD]

    except PyMongoError:
        raise ConnectDatabaseError('Error while retrieving group name for _id :' + str(groupID))

def removeCandidateFromGroups(candID: str, groupsID: list) -> None:
    collection = db.getCollection(GROUPS_DOCUMENT)
    try:
        for g in groupsID:
            collection.update({
                '_id': ObjectId(g)}, {
                '$pull': {
                    GROUPS_CANDIDATES_IDS_FIELD: ObjectId(candID)
                },
            })
    except PyMongoError:
        raise ConnectDatabaseError('Error while removing user with _id : ' + str(candID) + ' from groups.')


def getCandSubForGroupID(candID: str, groupsID: str) -> list:
    collection = db.getCollection(GROUPS_DOCUMENT)
    submissions = []
    try:
        for g in groupsID:
            groupAssignments = collection.find_one({'_id': ObjectId(g)})[GROUPS_ASSIGNMENTS_FIELD]
            for assign in groupAssignments:
                for sub in assign[GROUPS_ASSIGNMENTS_SUB_ID]:
                    submission = getSubmissionFromID(sub)
                    if submission is None: continue
                    if submission[ASSIGNMENT_SUB_CAND_ID] == candID:
                        submissions.append(submission)

        return submissions
    except PyMongoError:
        raise ConnectDatabaseError('Error while retrieving candidate submissions.')

def getGroupFromId(groupID: str) -> GROUP_TEMPLATE:
    collection = db.getCollection(GROUPS_DOCUMENT)
    try:
        result = collection.find_one({
            '_id': ObjectId(groupID)
        })
        return result
    except PyMongoError:
        raise ConnectDatabaseError('Error while retriving the group _id :' + str(groupID))

# def getAllEvalGroups(mail : str) -> list:
#     returnedList = []
#     try:
#         evaluator = getEvalFromMail(mail)
#         for g in evaluator[EVALUATOR_GROUPS_FIELD]:
#             group = getGroupFromId(g)
#             returnedList.append(group)
#         return returnedList
#     except PyMongoError :
#         raise ConnectDatabaseError('Error while retrieving groups for user with mail : ' + mail)


def getAllCandidateGroups(candidate : CANDIDATES_ITEM_TEMPLATE) -> list:
    collection = db.getCollection(GROUPS_DOCUMENT)
    returnedList = []
    try:
        for g in candidate[CANDIDATES_GROUPS_FIELD]:
            gObject = collection.find_one({
                '_id': ObjectId(g)
            })
            if gObject is None: raise GroupDoesNotExistException('Group with the _id : ' + str(g) + ' does not exists')
            returnedList.append({
                'id': str(g),
                GROUPS_NAME_FIELD: gObject[GROUPS_NAME_FIELD],
            })
        return returnedList
    except PyMongoError:
        raise ConnectDatabaseError('Error while retrieving groups')

def updateGroupName(groupID: str, newName: str) -> bool:
    collection = db.getCollection(GROUPS_DOCUMENT)
    try:
        result = collection.find_one_and_update({
            '_id': ObjectId(groupID)
        }, {
            '$set': {
                GROUPS_NAME_FIELD: newName
            }
        })
        return result is not None
    except PyMongoError:
        raise ConnectDatabaseError('Error while updating the ')