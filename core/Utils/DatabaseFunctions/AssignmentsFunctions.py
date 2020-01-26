"""
    This file will contains all of the functions that need to call the database
    to retrieve assignments data.
"""
from datetime import datetime
from core.Utils.Constants.DatabaseConstants import *
from core.Utils.DatabaseHandler import DatabaseHandler
from bson import ObjectId

db = DatabaseHandler()
db.connect()


def addAssignment(evalualor: EVALUATORS_ITEM_TEMPLATE, assignName: str, assignDeadLine: datetime, assignDesc: str) -> str:
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
    collection.find_one_and_update({'_id':ObjectId(assignID)}, {'$set': {ASSIGNMENT_FILENAME: filename}})
    db.close()
