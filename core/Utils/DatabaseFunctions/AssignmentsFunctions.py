"""
    This file will contains all of the functions that need to call the database
    to retrieve assignments data.
"""
from datetime import datetime

from core.Utils.Constants.DatabaseConstants import *
def addAssignment(evalualor: EVALUATORS_ITEM_TEMPLATE, assignName: str, assignDeadLine: datetime, assignDesc: str) -> bool:
    assignment = ASSIGNMENT_ITEM_TEMPLATE
    assignment[ID]