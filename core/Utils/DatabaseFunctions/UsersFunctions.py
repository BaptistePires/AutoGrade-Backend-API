"""
    This file will contains all of the functions that need to call the databse
    to retrieve users data.
"""
from core.Utils.DatabaseHandler import DatabaseHandler
from core.Utils.Constants.DatabaseConstants import *
from bson import ObjectId
from core.Utils.Exceptions.WrongUserTypeException import WrongUserTypeException
from core.Utils.Constants.DatabaseConstants import USERS_ITEM_TEMPLATE, CANDIDATES_ITEM_TEMPLATE
from pymongo.errors import PyMongoError
from core.Utils.Exceptions.ConnectDatabaseError import ConnectDatabaseError
from core.Utils.DatabaseFunctions.GroupsFunctions import *
from datetime import datetime

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
    try:
        eval = collection.find_one({'user_id': ObjectId(userId)})
        return eval
    except PyMongoError:
        raise ConnectDatabaseError('Error while getting the user with it\'s _id')


def getOneUserByMail(mail: str) -> USERS_ITEM_TEMPLATE:
    """
        Retrieve a user from the databse with a mail.
    :param mail: Mail of the user as string.
    :return: Dictionary representing the user form the database.
    """

    try:
        collection = db.getCollection(USERS_DOCUMENT)
        db.close()
        return collection.find_one({MAIL_FIELD: mail})
    except PyMongoError:
        raise ConnectDatabaseError('Error while getting the user with his email')


def getEvalFromMail(mail: str) -> dict:
    """
        Retrieve an evaluator object from the database with his mail address.
    :param mail: Mail as string.
    :return: Dictionary representing the user from the databse.
    """

    try:
        userEntity = getOneUserByMail(mail.lower())
        if userEntity is None: return None
        if userEntity[TYPE_FIELD] != EVALUATOR_TYPE: raise WrongUserTypeException("This user is not an evaluator.")
        return getEvalByUserId(userEntity['_id'])
    except PyMongoError:
        raise ConnectDatabaseError('')


# Candidates functions #
def getCandidateByUserId(userId: str) -> CANDIDATES_ITEM_TEMPLATE:
    collection = db.getCollection(CANDIDATES_DOCUMENT)
    cand = collection.find_one({USER_ID_FIELD: ObjectId(userId)})

    return cand


def getCandidateFromMail(mail: str) -> CANDIDATES_ITEM_TEMPLATE:
    collection = db.getCollection(CANDIDATES_DOCUMENT)
    try:
        user = getOneUserByMail(mail)
        if user is None: return None
        if user[TYPE_FIELD] != CANDIDATE_TYPE: raise WrongUserTypeException('This user is not a candidate')
        return getCandidateByUserId(user['_id'])
    except PyMongoError:
        raise ConnectDatabaseError('Error while retrieving candidate')


def addCandidate(mail: str, groupId: str) -> None:
    try:
        userCollection = db.getCollection(USERS_DOCUMENT)
        candCollection = db.getCollection(CANDIDATES_DOCUMENT)
        user = USERS_ITEM_TEMPLATE
        user[MAIL_FIELD] = mail
        user[TYPE_FIELD] = CANDIDATE_TYPE
        user[CONFIRMED_FIELD] = False
        user[CREATED_TIMESTAMP] = datetime.now().timestamp()
        idUser = db.insert(USERS_DOCUMENT, user.copy())
        candidate = CANDIDATES_ITEM_TEMPLATE
        candidate[USER_ID_FIELD] = idUser.inserted_id
        cand = db.insert(CANDIDATES_DOCUMENT, candidate.copy())
        updated = addGroupToCandidate(str(cand.inserted_id), groupId)
    except PyMongoError:
        raise ConnectDatabaseError('Error while adding the candidate to the database.')


def registerCandidate(candidate: CANDIDATES_ITEM_TEMPLATE, user: USERS_ITEM_TEMPLATE) -> None:
    userCollection = db.getCollection(USERS_DOCUMENT)
    candCollection = db.getCollection(CANDIDATES_DOCUMENT)
    try:
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
    except PyMongoError:
        raise ConnectDatabaseError('Error while registering the candidate.')
    if update is None: return False
    return True


def doesCandidateExists(mail) -> bool:
    user = getOneUserByMail(mail)
    if user is None:
        return False
    candidate = getCandidateByUserId(user['_id'])

    if candidate is None: return False

    return True


def addGroupToCandidate(idCand: str, idGroup: str) -> bool:
    candCollection = db.getCollection(CANDIDATES_DOCUMENT)
    groupCollection = db.getCollection(GROUPS_DOCUMENT)
    try:
        candCollection.find_one_and_update({'_id': ObjectId(idCand)},
                                           {'$push': {CANDIDATES_GROUPS_FIELD: ObjectId(idGroup)}})
        groupCollection.find_one_and_update({'_id': ObjectId(idGroup)},
                                            {'$push': {GROUPS_CANDIDATES_IDS_FIELD: ObjectId(idCand)}})
        return True
    except PyMongoError:
        raise ConnectDatabaseError('Error while adding candidate to the group.')


def getUserById(userId: str) -> USERS_ITEM_TEMPLATE:
    collection = db.getCollection(USERS_DOCUMENT)
    try:
        result = collection.find_one({'_id': ObjectId(userId)})
        return result
    except PyMongoError:
        raise ConnectDatabaseError('Error while getting the user bu it\'s _id')


def getGroupFromId(idGroup: str) -> GROUP_TEMPLATE:
    collection = db.getCollection(GROUPS_DOCUMENT)

    try:
        result = collection.find_one({'_id': ObjectId(idGroup)})
        return result
    except PyMongoError:
        raise ConnectDatabaseError('Error while getting the group form the _id')


def addGroupToEval(evalId: str, groupId: str) -> None:
    collection = db.getCollection(EVALUATORS_DOCUMENT)
    try:
        collection.find_one_and_update({'_id': ObjectId(evalId)},
                                       {'$push': {EVALUATOR_GROUPS_FIELD: ObjectId(groupId)}})
    except PyMongoError:
        raise ConnectDatabaseError('Error while adding group to the evaluator.')


def getAllGroupNameFromEvalId(evalId: str) -> list:
    try:
        groups = [{
            'id': str(g['_id']),
            GROUPS_NAME_FIELD: g[GROUPS_NAME_FIELD]
        } for g in getAllEvalGroups(evalId)]
        return groups
    except PyMongoError:
        raise ConnectDatabaseError('Error while groups name for an evaluator')


def getAllEvalGroups(evalID: str) -> list:
    collection = db.getCollection(EVALUATORS_DOCUMENT)
    try:
        evaluator = collection.find_one({
            '_id': ObjectId(evalID)
        })
        groups = [getGroupFromId(gID) for gID in evaluator[EVALUATOR_GROUPS_FIELD]]
        return groups
    except PyMongoError:
        raise ConnectDatabaseError('Error while retrieving groups for evaluator with the _id : ' + str(evalID))


def deleteCandidate(candID: str) -> None:
    collection = db.getCollection(CANDIDATES_DOCUMENT)
    try:
        collection.delete_one({
            '_id': ObjectId(candID)
        })
    except PyMongoError:
        raise ConnectDatabaseError('There was an error while deleting user with the _id : ' + str(candID))


def deleteUser(userID: str) -> None:
    collection = db.getCollection(USERS_DOCUMENT)
    try:
        collection.delete_one({
            '_id': ObjectId(userID)
        })
    except PyMongoError:
        raise ConnectDatabaseError('There was an error while deleting user with the _id : ' + str(userID))


def getEvalById(evalID: str) -> EVALUATORS_ITEM_TEMPLATE:
    collection = db.getCollection(EVALUATORS_DOCUMENT)
    try:
        return collection.find_one({
            '_id': ObjectId(evalID)
        })
    except PyMongoError:
        raise ConnectDatabaseError('Error while retrieving evaluator with the _id : ' + str(evalID))


def getCandidateById(candID: str) -> CANDIDATES_ITEM_TEMPLATE:
    collection = db.getCollection(CANDIDATES_DOCUMENT)
    try:
        return collection.find_one({
            '_id': ObjectId(candID)
        })
    except PyMongoError:
        raise ConnectDatabaseError('Error while retrieving the candidate with the _id : ', str(candID))


def updateUserFields(userID: str, fieldsToUpdate: object) -> bool:
    print(fieldsToUpdate)
    collection = db.getCollection(USERS_DOCUMENT)
    try:
        result = collection.find_one_and_update({
            '_id': ObjectId(userID)
        }, {
            '$set': fieldsToUpdate
        })
        return result
    except PyMongoError:
        raise ConnectDatabaseError('Error while updating user with the id : ' + set(userID))


def incEvalCorrectionsAllowed(evaluatorID: str, order_id: str, amount: int) -> None:
    collection = db.getCollection(EVALUATORS_DOCUMENT)

    try:
        r =  collection.find_one_and_update({
            '_id': ObjectId(evaluatorID)
        }, {
            '$inc': {
                EVALUATOR_CORRECTED_PROGRAM_LEFT_NAME: amount
            },
            '$push': {
                EVALUATOR_REGISTERED_TRANSACTIONS: ObjectId(order_id)
            }
        })
        return r

    except PyMongoError:
        raise ConnectDatabaseError(
            'Error while decrementing counter of correction allowed for evaluator : ' + str(evaluatorID))


def decrEvalCorrectionsAllowedFromID(evaluatorID: str) -> None:
    collection = db.getCollection(EVALUATORS_DOCUMENT)

    try:
        r =  collection.find_one_and_update({
            '_id': ObjectId(evaluatorID)
        }, {
            '$inc': {
                EVALUATOR_CORRECTED_PROGRAM_LEFT_NAME: -1
            }
        })
        return r
    except PyMongoError:
        raise ConnectDatabaseError(
            'Error while decrementing counter of correction allowed for evaluator : ' + str(evaluatorID))


def getAllCandidateSub(candidateID: str) -> list:
    print(candidateID)
    collection = db.getCollection(ASSIGNMENT_SUBMISSIONS_DOCUMENT)
    try:
        return collection.find({
            ASSIGNMENT_SUB_CAND_ID: ObjectId(candidateID)
        })
    except PyMongoError:
        raise ConnectDatabaseError('Error while retrieving candidate submissions')


def setEvalPremium(evaluatorID: str) -> None:
    collection = db.getCollection(EVALUATORS_DOCUMENT)

    try:
        return collection.find_one_and_update({
            '_id': ObjectId(evaluatorID)
        }, {
            '$set': {
                EVALUATOR_IS_PREMIUM: True
            }
        })

    except PyMongoError:
        raise ConnectDatabaseError('rror while setting account to premium ' + set(evaluatorID))
