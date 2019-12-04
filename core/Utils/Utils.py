import bcrypt
import jwt
import datetime
from os import getenv
from core.Utils.Exceptions.InvalidTokenException import InvalidTokenException
from core.Utils.Exceptions.ExpiredTokenException import ExpiredTokenException

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

def encodeAuthToken(user_id):
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
        }

        return jwt.encode(payload, getSecretKey(), algorithm='HS256').decode('utf-8')
    except Exception as e:
        print(e.args) # TODO : Raise the right expection

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
