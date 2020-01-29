import bcrypt
import jwt
from datetime import datetime, timedelta
import smtplib
import ssl
from werkzeug import datastructures
from itsdangerous import URLSafeTimedSerializer
from core.Utils.Constants.DatabaseConstants import *
from core.Utils.Constants.PathsFilesConstants import *
from os import getenv, path, sep, mkdir, remove
from core.Utils.Exceptions.InvalidTokenException import InvalidTokenException
from core.Utils.Exceptions.ExpiredTokenException import ExpiredTokenException
from core.Utils.Exceptions.FileExtNotAllowed import FileExtNotAllowed
from core.Utils.Exceptions.WrongIOsFormat import WrongIOsFormat
from core.Utils.Exceptions.EvaluatorDoesNotExist import EvaluatorDoesNotExist

from validate_email import validate_email
from core.Utils.DatabaseHandler import DatabaseHandler
from functools import wraps
from core.Utils.Constants.Constants import *
from flask import request
from core.Utils.DatabaseFunctions.AssignmentsFunctions import *
from core.Utils.Constants.ApiResponses import *
from core.Utils.DatabaseFunctions.GroupsFunctions import *
from core.Utils.DatabaseFunctions.UsersFunctions import *
# TEMP CONSTANT -> MOVED LATER
EMAIL_CONFIRM_KEY = 'ab50c025b8fbd3a9f76f8cf872a7b2369b1ba3cb6e8e6c7d'


####################
# System functions #
####################
def getSecretKey():
    """
        Retrieve secret key from the env.
    :return: The secret key has String.
    """
    return str(getenv('API_AUTO_GRADE_SECRET_KEY'))


###########################
# Users related functions #
###########################

def hashStr(strToHash: str) -> str:
    """
        This function hash the param str
    :param str: String to hash.
    :return: Hashed str.
    """
    salt = bcrypt.gensalt(5)
    return bcrypt.hashpw(strToHash.encode('utf-8'), salt)


def checkPw(clearPw: str, hashedPw: str) -> str:
    """
        Check if the hash of the password (clearPw) is the same that the hash provided (hashedPw).
    :param clearPw: A clear password that need to be validate.
    :param hashedPw: A hash that will be compared to the hash of the clear password.
    :return: boolean True if the password match otherwise false.
    """
    return bcrypt.checkpw(clearPw.encode('utf-8'), hashedPw)


def checkEmailFormat(mail: str) -> bool:
    """
        Validate an email.
    :param mail: Email to validate.
    :return: True if it's valide otherwise false.
    """
    return validate_email(email=mail)


def encodeAuthToken(mail: str) -> str:
    """
        Encode a mail in a token. Used to generate API keys.
    :param mail: Mail to put in the token.
    :return: The token as a String.
    """
    try:
        payload = {
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow(),
            'sub': mail
        }

        return jwt.encode(payload, getSecretKey(), algorithm='HS256').decode('utf-8')
    except Exception as e:
        print(e.args)  # TODO : Raise the right exception


def decodeAuthToken(token: str) -> str:
    """
        Decode a token created with encodeAuthToken function.
    :param token: Token to decode.
    :return: Mail address encoded in the token.
    """
    try:
        payload = jwt.decode(token.encode('utf-8'), getSecretKey())
        return payload['sub']
    except jwt.ExpiredSignature:
        raise ExpiredTokenException("Le token a expiré.", None)
    except jwt.InvalidTokenError:
        raise InvalidTokenException("Le token fournit est invalide.", None)


def isTokenValid(token, userId) -> bool:
    decodedToken = decodeAuthToken(token)
    if decodedToken != userId:
        raise InvalidTokenException("Le token fournit n'est pas valide.", None)
    return True


# Register confirmation functions
def generateMailConfToken(mail: str) -> str:
    """
        Generate the confirmation token to confirm an account.
    :param mail: Mail that need to confirmed.
    :return: Token as a string.
    """
    ts = URLSafeTimedSerializer(getSecretKey())
    return ts.dumps(mail, salt=EMAIL_CONFIRM_KEY)


def validateConfToken(token: str) -> str:
    """
        Retrieve the mail from the confirmation token generated with the function generateMailConfToken.
    :param token: Token as a string.
    :return: The mail encoded in the token.
    """
    ts = URLSafeTimedSerializer(getSecretKey())
    try:
        mail = ts.loads(token, salt=EMAIL_CONFIRM_KEY, max_age=172800)
        return mail
    except Exception as e:
        # TODO : Raise good expcetion here to say that the token does not match
        print(e)


# end

def isAccountValidated(userMail: str) -> str:
    """
        This function is used to check if a user has validate or not is account.
    :param userMail: Mail of the user in the database.
    :return: Boolean true if valide otherwise false.
    """
    db = DatabaseHandler()
    try:
        db.connect()
    except Exception as e:
        print("Can't connt to the database")
        return False

    user = db.getOneUserByMail(userMail)
    if user is None: return False
    if 'confirmed' in user: return user['confirmed']
    return False


def setupUserDictFromHTTPPayload(payload: dict, type: str) -> dict:
    """
        Set up the dictionnary object that will be stored in the database.
    :param payload: Payload of the request.
    :param type: Represents the type of the user (evaluator or candidate)
    :return: It returns an updated dictionary with the payload data parsed in.
    """
    user = USERS_ITEM_TEMPLATE
    user[NAME_FIELD] = payload[NAME_FIELD]
    user[LASTNAME_FIELD] = payload[LASTNAME_FIELD]
    user[PASSWORD_FIELD] = hashStr(payload[PASSWORD_FIELD])
    user[MAIL_FIELD] = payload[MAIL_FIELD]
    user[CONFIRMED_FIELD] = False
    user[TYPE_FIELD] = type
    return user


def setUpUserDictForRegisterCandidate(baseUserDict: USERS_ITEM_TEMPLATE, apiPayload: dict):
    baseUserDict[NAME_FIELD] = apiPayload[NAME_FIELD]
    baseUserDict[LASTNAME_FIELD] = apiPayload[LASTNAME_FIELD]
    baseUserDict[PASSWORD_FIELD] = hashStr(apiPayload[PASSWORD_FIELD])
    baseUserDict[CONFIRMED_FIELD] = True
    baseUserDict['_id'] = str(baseUserDict['_id'])
    return baseUserDict


def token_requiered(func):
    """
        Allows the usage of the decorator @token-requiered in api routes.
    """

    @wraps(func)
    def decorated(*args, **kwargs):
        token = None
        if 'X-API-KEY' in request.headers:
            token = request.headers['X-API-KEY']

        if not token:
            return {"status": -1, 'error': 'Token obligatoire.'}

        try:
            decodeAuthToken(request.headers['X-API-KEY'])
        except ExpiredTokenException:
            return TOKEN_EXPIRED
        except InvalidTokenException:
            return INVALID_TOKEN

        return func(*args, **kwargs)

    return decorated


def validateToken(mail, token):
    """
        Check if that mail ('mail') is the same as the one encoded in the token.
    :param mail: Mail to check as string.
    :param token: Token generated with encodeAuthToken function.
    :return: True if mail and the mail in the token are the same, False otherwise.
    """
    mailFromToken = decodeAuthToken(token)
    return mail == mailFromToken

def parseUserInfoToDict(user: USERS_ITEM_TEMPLATE) -> dict:
    returnedData = {}
    returnedData[NAME_FIELD] = user[NAME_FIELD]
    returnedData[LASTNAME_FIELD] = user[LASTNAME_FIELD]
    returnedData[MAIL_FIELD] = user[MAIL_FIELD]
    returnedData[TYPE_FIELD] = user[TYPE_FIELD]
    if user[TYPE_FIELD] == EVALUATOR_TYPE:
        evaluator = getEvalByUserId(user['_id'])
        returnedData['groups'] = [getGroupNameFromId(g) for g in evaluator[EVALUATOR_GROUPS_FIELD]]
    else:
        candidate = getCandidateByUserId(user['_id'])
        returnedData['groups'] = [{
            GROUPS_NAME_FIELD:getGroupNameFromId(g),
            'id': str(g)
        }for g in candidate[CANDIDATES_GROUPS_FIELD]]
    return returnedData

def deleteCandidateProcedure(user: USERS_ITEM_TEMPLATE, candidate : CANDIDATES_ITEM_TEMPLATE) -> None:
    # TODO REMOVE REF OF ASSIGN SUBMISSION IN GROUP SUBMISSIONS
    groupsID = candidate[CANDIDATES_GROUPS_FIELD]
    submissionsObjects = getCandSubForGroupID(candID=candidate['_id'], groupsID=groupsID)
    deleteSubmissionsFiles(submissions=submissionsObjects)
    removeAssignmentsSubmissions(submissionsObjects)
    removeCandidateFromGroups(candidate['_id'], groupsID=groupsID)
    deleteCandidate(candidate['_id'])
    deleteUser(candidate[USER_ID_FIELD])

def formatAssignsForEval(assigns: list) -> EVALUATOR_ASSIGNMENT_RESPONSE_TEMPLATE:
    returnedList = []
    print(assigns)
    for a in assigns:
        returnedDic = {}
        returnedDic['id'] = str(a.get('_id'))
        returnedDic[ASSIGNMENT_NAME] = a[ASSIGNMENT_NAME]
        returnedDic[ASSIGNMENT_DESCRIPTION] = a[ASSIGNMENT_DESCRIPTION]
        returnedDic[ASSIGNMENT_IS_VALID] = a[ASSIGNMENT_IS_VALID]
        returnedDic[ASSIGNMENT_INPUT_OUTPUTS] = a[ASSIGNMENT_INPUT_OUTPUTS]
        returnedDic[ASSIGNMENT_STATISTICS_NAME] = a[ASSIGNMENT_STATISTICS_NAME]
        for sub in a[ASSIGNMENT_SUB_ASSIGN_ID]:
            pass
        returnedList.append(returnedDic)
    return returnedList

def formatGroupsForEval(groups: list, candidateID:str) -> dict:
    formatedList = []
    for g in groups:
        tmp = {}
        tmp['id'] = str(g['_id'])
        tmp[GROUPS_NAME_FIELD] = g[GROUPS_NAME_FIELD]
        tmp[GROUPS_ASSIGNMENTS_FIELD]= []
        assignLst = []
        for a in g[GROUPS_ASSIGNMENTS_FIELD]:
            assignLst.append(getAssignmentFromId(a[GROUPS_ASSIGNMENTS_IDS_FIELD]))
        tmp[GROUPS_ASSIGNMENTS_FIELD].append(formatAssignsForEval(assignLst, candidateID))
        formatedList.append(tmp)
    return formatedList

def formatGroupForCandidate(group: GROUP_TEMPLATE, candidateID: str) -> dict:
    formatedGroup = {}
    formatedGroup[GROUPS_NAME_FIELD] = group[GROUPS_NAME_FIELD]
    evaluator = getEvalById(group[GROUPS_ID_EVAL_FIELD])
    evaluatorUser = getUserById(evaluator[USER_ID_FIELD])
    if evaluatorUser is None: raise EvaluatorDoesNotExist('User with the _id '
                                                          '' + str(group[GROUPS_ID_EVAL_FIELD]) + ' does not exist anymore.')
    formatedGroup['evaluatorInfo'] = {
        NAME_FIELD: evaluatorUser[NAME_FIELD],
        LASTNAME_FIELD: evaluatorUser[LASTNAME_FIELD],
        MAIL_FIELD: evaluatorUser[MAIL_FIELD],
        ORGANISATION_FIELD: evaluator[ORGANISATION_FIELD]
    }
    assignsList = []
    for a in group[GROUPS_ASSIGNMENTS_FIELD]:
        assignsList.append(formatAssignForCandidate(a, candidateID))
    formatedGroup[GROUPS_ASSIGNMENTS_FIELD] = assignsList
    return formatedGroup

def formatAssignForCandidate(groupAssign: GROUPS_ASSIGNMENT_TEMPLATE, candidateID: str) -> dict:
    formatedAssign = {}
    assign = getAssignmentFromId(groupAssign[GROUPS_ASSIGNMENTS_IDS_FIELD])
    formatedAssign['id'] = str(groupAssign[GROUPS_ASSIGNMENTS_IDS_FIELD])
    formatedAssign[ASSIGNMENT_NAME] = assign[ASSIGNMENT_NAME]
    formatedAssign[ASSIGNMENT_DESCRIPTION] = assign[ASSIGNMENT_DESCRIPTION]
    evaluator = getEvalById(assign[ASSIGNMENT_AUTHOR_ID])
    formatedAssign[TYPE_FIELD] = formatEvaluatorForCandidate(evaluator)
    formatedAssign[ASSIGNMENT_DEADLINE] = str(groupAssign[GROUPS_ASSIGNMENTS_DEADLINE])
    formatedAssign['submission'] = None
    for s in groupAssign[GROUPS_ASSIGNMENTS_SUB_ID]:
        submission = getSubmissionFromID(s)
        if submission[ASSIGNMENT_SUB_CAND_ID] == candidateID:
            formatedAssign['submission'] = submission
            formatedAssign['submission']['id'] = str(formatedAssign['submission']['_id'])
            formatedAssign['submission'].pop('_id')
            formatedAssign['submission'].pop(ASSIGNMENT_SUB_CAND_ID)
            formatedAssign['submission'].pop(ASSIGNMENT_FILENAME)
            formatedAssign['submission'].pop(ASSIGNMENT_SUB_GROUP_ID)
            formatedAssign['submission'].pop(ASSIGNMENT_SUB_ASSIGN_ID)
            formatedAssign['submission'][ASSIGNMENT_SUB_DATE_TIME_STAMP] = str(formatedAssign['submission'][ASSIGNMENT_SUB_DATE_TIME_STAMP])

            break

    print(formatedAssign)
    return formatedAssign


def formatEvaluatorForCandidate(evaluator: EVALUATORS_ITEM_TEMPLATE) -> dict:
    evaluatorUser = getUserById(evaluator[USER_ID_FIELD])
    return {
        NAME_FIELD: evaluatorUser[NAME_FIELD],
        LASTNAME_FIELD: evaluatorUser[LASTNAME_FIELD],
        MAIL_FIELD: evaluatorUser[MAIL_FIELD]
    }
###########################
# Files related functions #
###########################
def isFileAllowed(filename: str, allowedExt: list) -> bool:
    """
        Function test if the file is 'safe'. The allowedExt represents the files extention
        allowed, it must be a list of extention without the dot : ['py', 'java', ...].
        Return true if the file is OK otherwise return False.
    :return:
    """
    return '.' in filename and filename.count('.') == 1 and filename.rsplit('.', 1)[1].lower() in allowedExt


def getFileExt(filename):
    return filename.split('.')[1]


def createFolderForUserId(userId: str) -> None:
    """
    TODO : Implements user type checking -> create folder /xxx/xxx/{candidate / evaluator}/
        Create the folder that will be used to store user's assignments.
    :param userId: Id of the user as a string.
    :return: None
    """
    if not path.exists(ASSIGMENTS_DIR): mkdir(ASSIGMENTS_DIR)
    userId = str(userId)
    if path.exists(ASSIGMENTS_DIR + sep + userId):
        raise Exception
    else:
        mkdir(ASSIGMENTS_DIR + sep + userId)


def createFolderForGroup(groupId: str) -> None:
    if not path.exists(FILES_FOLDER_PATH): mkdir(FILES_FOLDER_PATH)
    if not path.exists(GROUPS_DIR_PATH): mkdir(GROUPS_DIR_PATH)
    folderPath = GROUPS_DIR_PATH + sep + str(groupId)
    if not path.exists(folderPath): mkdir((folderPath))


def createFolderAssignmentForGroup(groupId: str, assignID: str) -> None:
    createAssignmentFolder(groupId)
    if not path.exists(GROUPS_DIR_PATH + sep + str(groupId) + sep + str(assignID)): mkdir(
        GROUPS_DIR_PATH + sep + str(groupId) + sep + str(assignID))


def createAssignmentFolder(assignId: str) -> str:
    """
        This function create the folder for an assignment.
    :param assignId: Id of the assigment in the database.
    :return: None.
    """
    if not path.exists(FILES_FOLDER_PATH): mkdir(FILES_FOLDER_PATH)
    if not path.exists(FILES_FOLDER_PATH + sep + ASSIGMENTS_DIR): mkdir(FILES_FOLDER_PATH + sep + ASSIGMENTS_DIR)
    if not path.exists(FILES_FOLDER_PATH + sep + ASSIGMENTS_DIR + sep + str(assignId)): mkdir(
        FILES_FOLDER_PATH + sep + ASSIGMENTS_DIR + sep + str(assignId))
    return FILES_FOLDER_PATH + sep + ASSIGMENTS_DIR + sep + str(assignId)


def checkAndSaveFile(file: datastructures.FileStorage, assignID: str) -> None:
    filepath = createAssignmentFolder(str(assignID))
    if not isFileAllowed(file.filename, ALLOWED_FILES_EXT): raise FileExtNotAllowed('File extension not allowed.')
    saveFileName = BASE_FILE_NAME + '.' + getFileExt(file.filename)
    file.save(path.join(filepath, saveFileName))
    updateAssignFilename(assignID=assignID, filename=saveFileName)


def checkAndSaveIOs(ios: list, assignID: str) -> None:
    ios = ios[0].split(',')
    ios = [io.replace('"', '') for io in ios]
    toSaveIos = {}
    for io in ios:
        if not ':' in io or len(io) < 3 or io.count(':') > 1: raise WrongIOsFormat('Wrong IOS format for :' + io)
        i, o = io.split(':')
        if o[0] == ' ': o = o[1:]
        if len(i) < 1 or len(o) < 1: raise WrongIOsFormat('Wrong IOS format for : ' + io)
        toSaveIos[i] = o
    # Save ios je suis partie dormir lol
    saveIOS(ios=toSaveIos, assignID=assignID)

def isFileSafeAndAllowed(file: datastructures.FileStorage) -> bool:
    name, ext = file.filename.split('.')
    if ext not in ALLOWED_FILES_EXT: return False

def saveSubmissionFile(assignID: str, candID: str, groupID: str, file:datastructures.FileStorage) -> str:
    if not path.exists(GROUPS_DIR_PATH + sep + str(groupID) + sep + str(assignID)): raise CantSaveFile(
        'Can\'t save the current file, either the assignment does not exists or the group.')
    saveFileName = str(groupID) + '_' + str(candID) + '.' + file.filename.split('.')[1]
    file.save(path.join(GROUPS_DIR_PATH + sep + str(groupID) + sep + str(assignID), saveFileName))

    return saveFileName

def deleteSubmissionsFiles(submissions: dict) -> None:
    for s in submissions:
        fullPath = GROUPS_DIR_PATH + sep + s[ASSIGNMENT_SUB_ASSIGN_ID] + sep + str(s[ASSIGNMENT_FILENAME])
        if path.exists(fullPath): remove(fullPath)

#########################
# Date related funcions #
#########################

def isDateBeforeNow(date: datetime) -> bool:
    now = datetime.now()
    delta = date - now
    return delta.total_seconds() < 0


#########################
# Assignments functions #
#########################
def isAssignmnetAssignedToGroup(groupAssigns: dict, assignID: str) -> bool:
    if len(groupAssigns) < 1: return False
    for assign in groupAssigns:
        print(assign)
        if assign[GROUPS_ASSIGNMENTS_IDS_FIELD] == assignID:
            return True
    return False
