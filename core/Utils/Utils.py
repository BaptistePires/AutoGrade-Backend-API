import bcrypt
import jwt
from datetime import datetime, timedelta
from time import time
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
from core.Utils.Exceptions.WrongMarkingScheme import WrongMarkingScheme
from core.Utils.Exceptions.AmountNotAllowed import AmountNotAllowed
from core.Utils.Exceptions.PayPalConnectError import PayPalConnectError
from core.Utils.Exceptions.CantSaveFileException import CantSaveFileException
import requests
from validate_email import validate_email
from core.Utils.DatabaseHandler import DatabaseHandler
from functools import wraps
from core.Utils.Constants.Constants import *
from flask import request
from core.Utils.DatabaseFunctions.AssignmentsFunctions import *
from core.Utils.Constants.ApiResponses import *
from core.Utils.DatabaseFunctions.GroupsFunctions import *
from core.Utils.DatabaseFunctions.UsersFunctions import *
from re import search
from core.Utils.Constants.Constants import PAYPAL_CLT, PAYPAL_SCT, CORRECTIONS_PRICING

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


def validatePassword(password: str) -> bool:
    """
        Function to validate password.
        Conditions : Length 8 - 20, mut contains at least one lower case letter, one upper case letter, one number
        and one special character.
    """
    return search('(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%]).{8,20}', password)


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


###################################
# Register confirmation functions #
###################################
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
    user[MAIL_FIELD] = payload[MAIL_FIELD].lower()
    user[CONFIRMED_FIELD] = True
    user[TYPE_FIELD] = type
    user[CREATED_TIMESTAMP] = datetime.now().timestamp()
    return user


def setUpUserDictForRegisterCandidate(baseUserDict: USERS_ITEM_TEMPLATE, apiPayload: dict):
    """
        This method sets up a dict that will be stored in the database for the candidate.
    :param baseUserDict:  Dict to fill with the api payload values.
    :param apiPayload: Data retrieve from an api route.
    :return: baseUserDict filled.
    """
    baseUserDict[NAME_FIELD] = apiPayload[NAME_FIELD]
    baseUserDict[LASTNAME_FIELD] = apiPayload[LASTNAME_FIELD]
    baseUserDict[PASSWORD_FIELD] = hashStr(apiPayload[PASSWORD_FIELD])
    baseUserDict[CONFIRMED_FIELD] = True
    baseUserDict['_id'] = str(baseUserDict['_id'])
    baseUserDict[CREATED_TIMESTAMP] = str(baseUserDict[CREATED_TIMESTAMP])
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
    """
        This method is used to parse the info a user depending on his type.
    :param user:
    :return:
    """
    returnedData = {}
    returnedData[NAME_FIELD] = user[NAME_FIELD]
    returnedData[LASTNAME_FIELD] = user[LASTNAME_FIELD]
    returnedData[MAIL_FIELD] = user[MAIL_FIELD]
    returnedData[TYPE_FIELD] = user[TYPE_FIELD]
    returnedData[CREATED_TIMESTAMP] = user[CREATED_TIMESTAMP]

    if user[TYPE_FIELD] == EVALUATOR_TYPE:
        evaluator = getEvalByUserId(user['_id'])
        returnedData['groups'] = [getGroupNameFromId(g) for g in evaluator[EVALUATOR_GROUPS_FIELD]]
        returnedData[EVALUATOR_CORRECTED_PROGRAM_LEFT_NAME] = evaluator[EVALUATOR_CORRECTED_PROGRAM_LEFT_NAME]
        returnedData[EVALUATOR_IS_PREMIUM] = evaluator[EVALUATOR_IS_PREMIUM]
    else:
        candidate = getCandidateByUserId(user['_id'])
        returnedData['groups'] = [{
            GROUPS_NAME_FIELD: getGroupNameFromId(g),
            'id': str(g)
        } for g in candidate[CANDIDATES_GROUPS_FIELD]]
    return returnedData


def deleteCandidateProcedure(user: USERS_ITEM_TEMPLATE, candidate: CANDIDATES_ITEM_TEMPLATE) -> None:
    """
        This route is used to remove from the whole databse the existence of a candidate.
    :param user: User item from database of the candidate.
    :param candidate: Candidate item from the databse.
    :return:
    """
    # TODO REMOVE REF OF ASSIGN SUBMISSION IN GROUP SUBMISSIONS
    groupsID = candidate[CANDIDATES_GROUPS_FIELD]
    submissionsObjects = getCandSubForGroupID(candID=candidate['_id'], groupsID=groupsID)
    deleteSubmissionsFiles(submissions=submissionsObjects)
    removeAssignmentsSubmissions(submissionsObjects)
    removeCandidateFromGroups(candidate['_id'], groupsID=groupsID)
    deleteCandidate(candidate['_id'])
    deleteUser(candidate[USER_ID_FIELD])


def formatAssignsWithoutSubmissionsForEval(assigns: list) -> EVALUATOR_ASSIGNMENT_RESPONSE_TEMPLATE:
    """
        This method is used to format assignments for a evaluator without the candidate submissions in a user
        friendly way.
    :param assigns: List of Assignments item from the database.
    :return: List of formated assignments.
    """

    returnedList = []
    for a in assigns:
        returnedDic = {}
        returnedDic['id'] = str(a.get('_id'))
        returnedDic[ASSIGNMENT_NAME] = a[ASSIGNMENT_NAME]
        returnedDic[ASSIGNMENT_DESCRIPTION] = a[ASSIGNMENT_DESCRIPTION]
        returnedDic[ASSIGNMENT_IS_VALID] = a[ASSIGNMENT_IS_VALID]
        returnedDic[ASSIGNMENT_INPUT_OUTPUTS] = a[ASSIGNMENT_INPUT_OUTPUTS]
        returnedDic[ASSIGNMENT_STATISTICS_NAME] = a[ASSIGNMENT_STATISTICS_NAME]
        try:
            returnedDic[ASSIGNMENT_MARKING_SCHEME_NAME] = a[ASSIGNMENT_MARKING_SCHEME_NAME]
        except Exception:
            pass
        returnedList.append(returnedDic)

    return returnedList


def formatGroupsForEval(groups: list) -> dict:
    """
        This method format in a user friendly way the data of an evaluator groups.
    :param groups: List of Groups from database.
    :return: Formated groups.
    """
    formatedList = []
    for g in groups:
        tmp = {}
        tmp['id'] = str(g['_id'])
        tmp[GROUPS_NAME_FIELD] = g[GROUPS_NAME_FIELD]
        tmp[GROUPS_ASSIGNMENTS_FIELD] = []
        tmp[CREATED_TIMESTAMP] = str(g[CREATED_TIMESTAMP])
        assignLst = []
        for a in g[GROUPS_ASSIGNMENTS_FIELD]:
            print(a)
            assignLst.append(getAssignmentFromId(a[GROUPS_ASSIGNMENTS_IDS_FIELD]))
        tmp[GROUPS_ASSIGNMENTS_FIELD].append(formatAssignsWithoutSubmissionsForEval(assignLst))
        formatedList.append(tmp)
    return formatedList


def formatGroupForCandidate(group: GROUP_TEMPLATE, candidateID: str) -> dict:
    """
        This method format in a user friendly way the data of a candidate groups.
    :param group: List of Groups from the database.
    :param candidateID: Id of the current candidate.
    :return: Groups formated.
    """
    formatedGroup = {}
    formatedGroup[GROUPS_NAME_FIELD] = group[GROUPS_NAME_FIELD]
    evaluator = getEvalById(group[GROUPS_ID_EVAL_FIELD])
    evaluatorUser = getUserById(evaluator[USER_ID_FIELD])
    if evaluatorUser is None: raise EvaluatorDoesNotExist('User with the _id '
                                                          '' + str(
        group[GROUPS_ID_EVAL_FIELD]) + ' does not exist anymore.')
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
    """
        This function fully format an assignment to be displayed to a candidate.
    :param groupAssign: Item from the database. Represents all the groups assignments.
    :param candidateID: Id of the current candidate;
    :return: Formated assignments
    """
    formatedAssign = {}
    assign = getAssignmentFromId(groupAssign[GROUPS_ASSIGNMENTS_IDS_FIELD])
    formatedAssign['id'] = str(groupAssign[GROUPS_ASSIGNMENTS_IDS_FIELD])
    formatedAssign[ASSIGNMENT_NAME] = assign[ASSIGNMENT_NAME]
    formatedAssign[ASSIGNMENT_DESCRIPTION] = assign[ASSIGNMENT_DESCRIPTION]
    evaluator = getEvalById(assign[ASSIGNMENT_AUTHOR_ID])
    formatedAssign[EVALUATOR_TYPE] = formatEvaluatorForCandidate(evaluator)
    formatedAssign[ASSIGNMENT_DEADLINE] = str(groupAssign[GROUPS_ASSIGNMENTS_DEADLINE])
    formatedAssign[ASSIGNMENT_MARKING_SCHEME_NAME] = assign[ASSIGNMENT_MARKING_SCHEME_NAME]
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
            formatedAssign['submission'][ASSIGNMENT_SUB_DATE_TIME_STAMP] = str(
                formatedAssign['submission'][ASSIGNMENT_SUB_DATE_TIME_STAMP])
            formatedAssign['submission'][CREATED_TIMESTAMP] = str(formatedAssign['submission'][CREATED_TIMESTAMP])
            break
    return formatedAssign


def formatEvaluatorForCandidate(evaluator: EVALUATORS_ITEM_TEMPLATE) -> dict:
    evaluatorUser = getUserById(evaluator[USER_ID_FIELD])
    return {
        NAME_FIELD: evaluatorUser[NAME_FIELD],
        LASTNAME_FIELD: evaluatorUser[LASTNAME_FIELD],
        MAIL_FIELD: evaluatorUser[MAIL_FIELD]
    }


def formatGroupForEval(group: GROUP_TEMPLATE, evaluatorID: str) -> dict:
    returnedGroup = {}
    returnedGroup['id'] = str(group['_id'])
    returnedGroup[GROUPS_NAME_FIELD] = group[GROUPS_NAME_FIELD]
    returnedGroup[CREATED_TIMESTAMP] = group[CREATED_TIMESTAMP]
    returnedGroup[GROUPS_ASSIGNMENTS_FIELD] = formatAssignsWithSubmissionsForEval(group[GROUPS_ASSIGNMENTS_FIELD])
    returnedGroup['candidates'] = formatCandidatesForEval(group[GROUPS_CANDIDATES_IDS_FIELD])
    return returnedGroup


def formatAssignsWithSubmissionsForEval(assignList: list) -> dict:
    formatedAssignments = []
    print(assignList)
    for a in assignList:
        tmpAssign = {}
        assign = getAssignmentFromId(a[GROUPS_ASSIGNMENTS_IDS_FIELD])
        print(assign)
        tmpAssign['id'] = str(a[GROUPS_ASSIGNMENTS_IDS_FIELD])
        tmpAssign[GROUPS_ASSIGNMENTS_DEADLINE] = str(a[GROUPS_ASSIGNMENTS_DEADLINE])
        tmpAssign[ASSIGNMENT_INPUT_OUTPUTS] = str(assign[ASSIGNMENT_INPUT_OUTPUTS])
        tmpAssign[ASSIGNMENT_STATISTICS_NAME] = assign[ASSIGNMENT_STATISTICS_NAME]
        tmpAssign[ASSIGNMENT_MARKING_SCHEME_NAME] = assign[ASSIGNMENT_MARKING_SCHEME_NAME]
        tmpAssign['submissions'] = []
        for s in a[GROUPS_ASSIGNMENTS_SUB_ID]:
            submission = getSubmissionFromID(s)
            tmpAssign['submissions'].append(formatSubmissionForEval(submission))

        formatedAssignments.append(tmpAssign)
    return formatedAssignments


def formatCandidatesForEval(candidatesIDs: list) -> list:
    formatedCandidates = []
    for c in candidatesIDs:
        tmpCandidate = {
            'id': None,
            NAME_FIELD: None,
            LASTNAME_FIELD: None,
            MAIL_FIELD: None,
            ORGANISATION_FIELD: None
        }
        candidate = getCandidateById(c)
        if candidate is not None:
            userCandidate = getUserById(candidate[USER_ID_FIELD])
            tmpCandidate['id'] = str(candidate['_id'])
            tmpCandidate[NAME_FIELD] = userCandidate[NAME_FIELD]
            tmpCandidate[LASTNAME_FIELD] = userCandidate[LASTNAME_FIELD]
            tmpCandidate[MAIL_FIELD] = userCandidate[MAIL_FIELD]
            tmpCandidate[ORGANISATION_FIELD] = candidate[ORGANISATION_FIELD]
        formatedCandidates.append(tmpCandidate)

    return formatedCandidates


def formatSubmissionForEval(submission: CANDIDATE_ASSIGNMENT_SUBMISSION_TEMPLATE) -> dict:
    tmpSub = {}
    candidate = getCandidateById(submission[ASSIGNMENT_SUB_CAND_ID])
    tmpSub[ASSIGNMENT_SUB_CAND_ID] = None
    if candidate is not None:
        tmpSub[ASSIGNMENT_SUB_CAND_ID] = str(candidate['_id'])
    tmpSub[ASSIGNMENT_SUB_DATE_TIME_STAMP] = str(submission[ASSIGNMENT_SUB_DATE_TIME_STAMP])
    tmpSub[ASSIGNMENT_STATISTICS_NAME] = submission[ASSIGNMENT_STATISTICS_NAME]
    tmpSub[ASSIGNMENT_SUB_GRADE] = submission[ASSIGNMENT_SUB_GRADE]
    return tmpSub


def paypalGetAuth2() -> str:
    baseUrl = 'https://api.sandbox.paypal.com/v1/oauth2/token'
    headers = {
        'Accept-Language': 'en_US',
        'Content-Type': 'x-www-form-urlencoded'
    }
    body = {
        'grant_type': 'client_credentials'
    }
    r = requests.post(baseUrl, headers=headers, data=body, auth=(PAYPAL_CLT, PAYPAL_SCT))
    if r.status_code == 200:
        return r.json()['access_token']
    raise PayPalConnectError('Error while connecting to the paypal API')


def validatePaypalTransaction(evaluatorID: str, orderID: str) -> bool:
    baseUrl = 'https://api.sandbox.paypal.com/v2/checkout/orders/{order_id}'.format(order_id=orderID)
    token = paypalGetAuth2()
    header = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {token}'.format(token=token)
    }
    r = requests.get(baseUrl, headers=header)
    data = r.json()
    if r.status_code == 200:
        if data['status'] == 'APPROVED':
            amount = int(float(data['purchase_units'][0]['amount']['value']))
            if int(amount) in CORRECTIONS_PRICING:
                incEvalCorrectionsAllowed(evaluatorID, orderID, CORRECTIONS_PRICING[int(amount)])
                return True
            else:
                raise AmountNotAllowed('The amount :' + str(amount) + ' is not authorized.')
    raise PayPalConnectError('Error while connecting to the paypal API')


def validatePremiumTransaction(evaluatorID: str, orderID: str) -> bool:


    baseUrl = 'https://api.sandbox.paypal.com/v2/checkout/orders/{order_id}'.format(order_id=orderID)
    token = paypalGetAuth2()
    header = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {token}'.format(token=token)
    }
    r = requests.get(baseUrl, headers=header)
    data = r.json()
    if r.status_code == 200:
        if data['status'] == 'COMPLETED':
            setEvalPremium(evaluatorID=evaluatorID)
            return True
        else:
            raise AmountNotAllowed('The amount :' + str(amount) + ' is not authorized.')
    raise PayPalConnectError('Error while connecting to the paypal API')


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


def isCorrectionAllowed(idEvaluaror: str) -> bool:
    eval = getEvalById(idEvaluaror)
    correctionsRemaining = int(eval[EVALUATOR_CORRECTED_PROGRAM_LEFT_NAME])
    return correctionsRemaining > 0


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


def saveSubmissionFile(assignID: str, candID: str, groupID: str, file: datastructures.FileStorage) -> str:
    if not path.exists(GROUPS_DIR_PATH + sep + str(groupID) + sep + str(assignID)): raise CantSaveFileException(
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

def isTimestampBeforeNow(dateTimestamp: float) -> bool:
    return dateTimestamp < datetime.now().timestamp()


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


def checkAndFormatMarkingSchemRqstArgs(requestArgs: dict) -> ASSIGNMENT_MARKING_SCHEME:
    formatedMS = ASSIGNMENT_MARKING_SCHEME
    try:
        cpuTimeMS = int(requestArgs.get(ASSIGNMENT_MARKING_SCHEME_NAME + '_' + ASSIGNMENT_STAT_TIME))
        fileSizeMS = int(requestArgs.get(ASSIGNMENT_MARKING_SCHEME_NAME + '_' + ASSIGNMENT_FILE_SIZE))
        memUsedMS = int(requestArgs.get(ASSIGNMENT_MARKING_SCHEME_NAME + '_' + ASSIGNMENT_MEMORY_USED))
    except KeyError:
        raise WrongMarkingScheme('Missing argument')
    if sum((cpuTimeMS, fileSizeMS, memUsedMS)) > 100: raise WrongMarkingScheme(
        'Sum of all the marking scheme is not 100')
    formatedMS[ASSIGNMENT_STAT_TIME] = cpuTimeMS
    formatedMS[ASSIGNMENT_FILE_SIZE] = fileSizeMS
    formatedMS[ASSIGNMENT_MEMORY_USED] = memUsedMS
    return formatedMS


def formatSubmissionsForCand(candidateID: str) -> list:
    allSubmissions = getAllCandidateSub(candidateID)
    formatedList = []
    for sub in allSubmissions:
        tmpDict = {}
        tmpDict['id'] = str(sub['_id'])
        tmpDict[ASSIGNMENT_SUB_GRADE] = sub[ASSIGNMENT_SUB_GRADE]
        group = getGroupFromId(sub[ASSIGNMENT_SUB_GROUP_ID])
        groupAssign = None
        for ag in group[GROUPS_ASSIGNMENTS_FIELD]:
            if ag[GROUPS_ASSIGNMENTS_IDS_FIELD] == sub[ASSIGNMENT_SUB_ASSIGN_ID]:
                tmpDict[GROUPS_ASSIGNMENTS_DEADLINE] = ag[ASSIGNMENT_DEADLINE]

        tmpDict['group'] = {
            'id': str(group['_id']),
            GROUPS_NAME_FIELD: group[GROUPS_NAME_FIELD]
        }
        formatedList.append(tmpDict)
    return formatedList
