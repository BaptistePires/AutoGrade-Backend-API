import bcrypt
import jwt
import datetime
import smtplib
import ssl
from itsdangerous import URLSafeTimedSerializer
from core.Utils.Constants.ApiModels import USERS_ITEM_TEMPLATE
from core.Utils.Constants.PathsConstants import ASSIGMENTS_DIR
from os import getenv, path, sep, mkdir
from core.Utils.Exceptions.InvalidTokenException import InvalidTokenException
from core.Utils.Exceptions.ExpiredTokenException import ExpiredTokenException
from validate_email import validate_email
from core.Utils.DatabaseHandler import DatabaseHandler
from functools import wraps
from flask import request

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
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2),
            'iat': datetime.datetime.utcnow(),
            'sub': mail
        }

        return jwt.encode(payload, getSecretKey(), algorithm='HS256').decode('utf-8')
    except Exception as e:
        print(e.args) # TODO : Raise the right exception

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

def createFolderForUserId(userId: str) -> None :
    """
        Create the folder that will be used to store user's assignments.
    :param userId: Id of the user as a string.
    :return: None
    """
    if not path.exists(ASSIGMENTS_DIR): mkdir(ASSIGMENTS_DIR)
    userId = str(userId)
    if path.exists(ASSIGMENTS_DIR + sep + userId): raise Exception
    else: mkdir(ASSIGMENTS_DIR + sep + userId)


def setupUserDictFromHTTPPayload(payload : dict, type: str) -> dict:
    """
        Set up the dictionnary object that will be stored in the database.
    :param payload: Payload of the request.
    :param type: Represents the type of the user (evaluator or candidate)
    :return: It returns an updated dictionary with the payload data parsed in.
    """
    user = USERS_ITEM_TEMPLATE
    user["name"] = payload["name"]
    user["lastname"] = payload["lastname"]
    user["password"] = hashStr(payload["password"])
    user["email"] = payload["email"]
    user["confirmed"] = False
    user["type"] = type
    return user

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
