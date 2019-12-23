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


# TEMP CONSTANT -> MOVED LATER
EMAIL_CONFIRM_KEY = 'ab50c025b8fbd3a9f76f8cf872a7b2369b1ba3cb6e8e6c7d'

####################
# System functions #
####################
def getSecretKey():
    return str(getenv('API_AUTO_GRADE_SECRET_KEY'))

###########################
# Users related functions #
###########################

def hashStr(strToHash):
    salt = bcrypt.gensalt(5)
    return bcrypt.hashpw(strToHash.encode('utf-8'), salt)

def checkPw(clearPw, hashedPw):
    return bcrypt.checkpw(clearPw.encode('utf-8'), hashedPw)

def checkEmailFormat(mail):
    return validate_email(email=mail)


def encodeAuthToken(user_id):
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
        }

        return jwt.encode(payload, getSecretKey(), algorithm='HS256').decode('utf-8')
    except Exception as e:
        print(e.args) # TODO : Raise the right exception

def decodeAuthToken(token):
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
def generateMailConfToken(mail):
    ts = URLSafeTimedSerializer(getSecretKey())
    return ts.dumps(mail, salt=EMAIL_CONFIRM_KEY)

def validateConfToken(token):
    ts = URLSafeTimedSerializer(getSecretKey())
    try:
        mail = ts.loads(token, salt=EMAIL_CONFIRM_KEY, max_age=172800)
        return mail
    except Exception as e:
        # TODO : Raise good expcetion here to say that the token does not match
        print(e)
# end
def createFolderForUserId(userId):
    if not path.exists(ASSIGMENTS_DIR): mkdir(ASSIGMENTS_DIR)
    userId = str(userId)
    if path.exists(ASSIGMENTS_DIR + sep + userId): raise Exception
    else: mkdir(ASSIGMENTS_DIR + sep + userId)


def setupUserDictFromHTTPPayload(payload):
    user = USERS_ITEM_TEMPLATE
    user["name"] = payload["name"]
    user["lastname"] = payload["lastname"]
    user["password"] = hashStr(payload["password"])
    user["email"] = payload["email"]
    user["confirmed"] = False
    return user