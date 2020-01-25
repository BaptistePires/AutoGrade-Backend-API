"""
    This file will contains all of the functions that need to call the databse
    to retrieve users data.
"""
from core.Utils.DatabaseHandler import DatabaseHandler
from core.Utils.Constants.DatabaseConstants import *
from bson import ObjectId
from core.Utils.Exceptions.WrongUserTypeException import WrongUserTypeException
from core.Utils.Constants.DatabaseConstants import USERS_ITEM_TEMPLATE, CANDIDATES_ITEM_TEMPLATE

db = DatabaseHandler()
db.connect()
# Evaluators functions #

def getEvalByUserId(userId: str) -> EVALUATORS_ITEM_TEMPLATE:
    """
        Retrieve Evaluator objects from the database from an id.
    :param userId: Id user as string. Converted as ObjectId inside the function.
    :return: Dictionary representing the evaluator from the database.
    """

    collection = db.getCollection(EVALUATORS_DOCUMENT)
    eval = collection.find_one({'user_id': ObjectId(userId)})
    
    return eval



def getOneUserByMail(mail: str) -> USERS_ITEM_TEMPLATE:
    """
        Retrieve a user from the databse with a mail.
    :param mail: Mail of the user as string.
    :return: Dictionary representing the user form the database.
    """

    collection = db.getCollection(USERS_DOCUMENT)
    
    return collection.find_one({MAIL_FIELD: mail})

def getEvalFromMail(mail: str) -> dict:
    """
        Retrieve an evaluator object from the database with his mail address.
    :param mail: Mail as string.
    :return: Dictionary representing the user from the databse.
    """

    userEntity = getOneUserByMail(mail.lower())
    if userEntity is None: return None
    if userEntity['type'] != EVALUATOR_TYPE: raise WrongUserTypeException("This user is not an evaluator.")
    
    return getEvalByUserId(userEntity['_id'])

# Candidates functions #
def getCandidateByUserId(userId: str) -> CANDIDATES_ITEM_TEMPLATE:

    collection = db.getCollection(CANDIDATES_DOCUMENT)
    cand = collection.find_one({'user_id': ObjectId(userId)})
    
    return cand

def addCandidate(mail: str, groupId: str) -> None:

    userCollection = db.getCollection(USERS_DOCUMENT)
    candCollection = db.getCollection(CANDIDATES_DOCUMENT)
    user = USERS_ITEM_TEMPLATE
    user[MAIL_FIELD] = mail
    user[TYPE_FIELD] = CANDIDATE_TYPE
    user[CONFIRMED_FIELD] = False
    idUser = db.insert(USERS_DOCUMENT, user.copy())
    candidate = CANDIDATES_ITEM_TEMPLATE
    candidate[USER_ID_FIELD] = idUser.inserted_id
    cand = db.insert(CANDIDATES_DOCUMENT, candidate.copy())
    updated = addGroupToCandidate(str(cand.inserted_id), groupId)
    

def registerCandidate(candidate : CANDIDATES_ITEM_TEMPLATE, user : USERS_ITEM_TEMPLATE) -> None:

    userCollection = db.getCollection(USERS_DOCUMENT)
    candCollection = db.getCollection(CANDIDATES_DOCUMENT)
    update = userCollection.find_one_and_update({'_id': ObjectId(user['_id'])}, {'$set': {
        NAME_FIELD: user[NAME_FIELD],
        LASTNAME_FIELD: user[LASTNAME_FIELD],
        PASSWORD_FIELD: user[PASSWORD_FIELD],
        CONFIRMED_FIELD: bool(user[CONFIRMED_FIELD])
    }})
    if update is None: return False
    update = candCollection.find_one_and_update({'_id': ObjectId(candidate['_id'])}, {'$set': {
        ORGANISATION_FIELD: candidate[ORGANISATION_FIELD]
    }})
    
    if update is None: return False
    return True

def doesCandidateExists(mail)-> bool:

    user = getOneUserByMail(mail)
    if user is None:
        
        return False
    candidate = getCandidateByUserId(user['_id'])
    
    if candidate is None: return False

    return True

def addGroupToCandidate(idCand: str, idGroup: str) -> bool:

    candCollection = db.getCollection(CANDIDATES_DOCUMENT)
    groupCollection = db.getCollection(GROUPS_DOCUMENT)
    candCollection.find_one_and_update({'_id': ObjectId(idCand)}, {'$push': {CANDIDATES_GROUPS_FIELD: ObjectId(idGroup)}} )
    groupCollection.find_one_and_update({'_id': ObjectId(idGroup)}, {'$push': {GROUPS_CANDIDATES_IDS_FIELD: ObjectId(idCand)}})
    

def getUserById(userId: str) -> USERS_ITEM_TEMPLATE:

    collection = db.getCollection(USERS_DOCUMENT)
    result = collection.find_one({'_id': ObjectId(userId)})
    
    return result

def getGroupFromId(idGroup: str) -> dict:

    collection = db.getCollection(GROUPS_DOCUMENT)
    result =  collection.find_one({'_id': ObjectId(idGroup)})
    
    return result
