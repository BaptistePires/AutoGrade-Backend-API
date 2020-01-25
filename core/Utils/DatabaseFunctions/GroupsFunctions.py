"""
    This file will contains all of the functions that need to call the database
    to retrieve groups data.
"""
from core.Utils.DatabaseHandler import DatabaseHandler
from core.Utils.Constants.DatabaseConstants import *
from bson import ObjectId
from core.Utils.Exceptions.GroupDoesNotExistException import GroupDoesNotExistException

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