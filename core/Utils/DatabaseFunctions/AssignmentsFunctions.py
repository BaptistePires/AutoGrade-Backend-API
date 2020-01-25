"""
    This file will contains all of the functions that need to call the database
    to retrieve assignments data.
"""
from datetime import datetime
from core.Utils.Constants.DatabaseConstants import *
from core.Utils.DatabaseHandler import DatabaseHandler

db = DatabaseHandler()
db.connect()


def addAssignment(evalualor: EVALUATORS_ITEM_TEMPLATE, assignName: str, assignDeadLine: datetime, assignDesc: str) -> str:
    assignment = ASSIGNMENT_ITEM_TEMPLATE
    assignment[ASSIGNMENT_AUTHOR_ID] = evalualor['_id']
    assignment[ASSIGNMENT_NAME] = assignName
    assignment[ASSIGNMENT_DESCRIPTION] = assignDesc
    assignment[ASSIGNMENT_DEADLINE] = assignDeadLine
    assignInserted = db.insert(ASSIGNMENTS_DOCUMENT, assignment.copy())
    return str(assignInserted.inserted_id)
