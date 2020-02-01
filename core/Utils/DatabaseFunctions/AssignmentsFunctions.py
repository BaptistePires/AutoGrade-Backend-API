"""
    This file will contains all of the functions that need to call the database
    to retrieve assignments data.
"""
from core.Utils.Constants.DatabaseConstants import *
from core.Utils.DatabaseHandler import DatabaseHandler
from bson import ObjectId, json_util
from core.Utils.Exceptions.ConnectDatabaseError import ConnectDatabaseError
from pymongo.errors import PyMongoError
from datetime import datetime

db = DatabaseHandler()


def addAssignment(evalualor: EVALUATORS_ITEM_TEMPLATE, assignName: str, assignDesc: str,
                  markingScheme: ASSIGNMENT_MARKING_SCHEME) -> str:
    assignment = ASSIGNMENT_ITEM_TEMPLATE
    assignment[ASSIGNMENT_AUTHOR_ID] = evalualor['_id']
    assignment[ASSIGNMENT_NAME] = assignName
    assignment[ASSIGNMENT_DESCRIPTION] = str(assignDesc)
    assignment[ASSIGNMENT_MARKING_SCHEME_NAME] = markingScheme
    assignment[CREATED_TIMESTAMP] = datetime.now().timestamp()
    try:
        db.connect()
        assignInserted = db.insert(ASSIGNMENTS_DOCUMENT, assignment)
        return str(assignInserted.inserted_id)
    except PyMongoError:
        raise ConnectDatabaseError('Error while adding an assignment')


def getAssignmentFromId(assignID: str) -> ASSIGNMENT_ITEM_TEMPLATE:
    db.connect()
    collection = db.getCollection(ASSIGNMENTS_DOCUMENT)
    try:

        assign = collection.find_one({'_id': ObjectId(assignID)})
        db.close()
        return assign
    except PyMongoError:
        raise ConnectDatabaseError('Error while getting assignment with the id ' + assignID)


def saveIOS(assignID: str, ios: list):
    try:
        db.connect()
        collection = db.getCollection(ASSIGNMENTS_DOCUMENT)
        collection.find_one_and_update({'_id': ObjectId(assignID)}, {'$set': {ASSIGNMENT_INPUT_OUTPUTS: ios}})
        db.close()
    except PyMongoError:
        raise ConnectDatabaseError('Error while saving Inputs/Outpus for the assignment : ' + assignID)


def updateAssignFilename(assignID: str, filename: str) -> None:
    collection = db.getCollection(ASSIGNMENTS_DOCUMENT)
    try:
        db.connect()
        collection.find_one_and_update({'_id': ObjectId(assignID)}, {'$set': {ASSIGNMENT_FILENAME: filename}})
        db.close()
    except PyMongoError:
        raise ConnectDatabaseError('Error while updating filename for the assignment with the id ' + assignID)


def getAllAssignmentsForEval(eval: EVALUATORS_ITEM_TEMPLATE) -> list:
    try:
        db.connect()
        collection = db.getCollection(ASSIGNMENTS_DOCUMENT)
        assigns = collection.find({ASSIGNMENT_AUTHOR_ID: ObjectId(eval['_id'])})
        db.close()
        return assigns
    except PyMongoError:
        raise ConnectDatabaseError('Error while connecting to the database')


def saveSubmission(assignID: str, groupID: str, candID: str, savedFilename: str, dateSub: float) -> str:
    submission = CANDIDATE_ASSIGNMENT_SUBMISSION_TEMPLATE
    submission[ASSIGNMENT_SUB_CAND_ID] = ObjectId(candID)
    submission[ASSIGNMENT_SUB_ASSIGN_ID] = ObjectId(assignID)
    submission[ASSIGNMENT_SUB_GROUP_ID] = ObjectId(groupID)
    submission[ASSIGNMENT_FILENAME] = savedFilename
    submission[ASSIGNMENT_SUB_DATE_TIME_STAMP] = dateSub
    submission[CREATED_TIMESTAMP] = datetime.now()
    try:
        db.connect()
        insertedSub = db.insert(ASSIGNMENT_SUBMISSIONS_DOCUMENT, submission.copy())
        db.close()
        return insertedSub.inserted_id
    except PyMongoError as e:
        raise ConnectDatabaseError('Errow hile saing submission : ' + str(e))


def removeAssignmentsSubmissions(submissionsID: list) -> None:
    collection = db.getCollection(ASSIGNMENT_SUBMISSIONS_DOCUMENT)
    try:
        db.connect()
        for s in submissionsID:
            collection.delete_one({'_id': ObjectId(s['_id'])})
        db.close()
    except PyMongoError:
        raise ConnectDatabaseError('Error while removing submission')


def getSubmissionFromID(subID: str) -> dict:
    try:
        db.connect()
        collection = db.getCollection(ASSIGNMENT_SUBMISSIONS_DOCUMENT)
        result = collection.find_one({'_id': ObjectId(subID)})
        db.close()
        return result
    except PyMongoError:
        raise ConnectDatabaseError('Error while retrieving submission with _id : ' + str(subID))
