"""
    This file will contains all of the functions that need to call the database
    to retrieve assignments data.
"""
from datetime import datetime
from core.Utils.Constants.DatabaseConstants import *
from core.Utils.DatabaseHandler import DatabaseHandler
from bson import ObjectId, json_util
from core.Utils.Exceptions.ConnectDatabaseError import ConnectDatabaseError
from pymongo.errors import PyMongoError

db = DatabaseHandler()


def addAssignment(evalualor: EVALUATORS_ITEM_TEMPLATE, assignName: str, assignDeadLine: datetime,
                  assignDesc: str) -> str:
    assignment = ASSIGNMENT_ITEM_TEMPLATE
    assignment[ASSIGNMENT_AUTHOR_ID] = evalualor['_id']
    assignment[ASSIGNMENT_NAME] = assignName
    assignment[ASSIGNMENT_DESCRIPTION] = assignDesc
    assignment[ASSIGNMENT_DEADLINE] = assignDeadLine
    assignInserted = db.insert(ASSIGNMENTS_DOCUMENT, assignment.copy())
    db.close()
    return str(assignInserted.inserted_id)


def getAssignmentFromId(assignID: str) -> ASSIGNMENT_ITEM_TEMPLATE:
    collection = db.getCollection(ASSIGNMENTS_DOCUMENT)
    assign = collection.find_one({'_id': ObjectId(assignID)})
    db.close()
    return assign


def saveIOS(assignID: str, ios: list):
    collection = db.getCollection(ASSIGNMENTS_DOCUMENT)
    collection.find_one_and_update({'_id': ObjectId(assignID)}, {'$set': {ASSIGNMENT_INPUT_OUTPUTS: ios}})
    db.close()


def updateAssignFilename(assignID: str, filename: str) -> None:
    collection = db.getCollection(ASSIGNMENTS_DOCUMENT)
    collection.find_one_and_update({'_id': ObjectId(assignID)}, {'$set': {ASSIGNMENT_FILENAME: filename}})
    db.close()


def getAllAssignmentsForEval(eval: EVALUATORS_ITEM_TEMPLATE) -> list:
    try:
        db.connect()
    except PyMongoError:
        raise ConnectDatabaseError('Error while connecting to the databse')
    collection = db.getCollection(ASSIGNMENTS_DOCUMENT)
    assigns = collection.find({ASSIGNMENT_AUTHOR_ID: ObjectId(eval['_id'])})
    print(assigns)
    return json_util.dumps(assigns)
