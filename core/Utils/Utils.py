import bcrypt
import unidecode

def hashStr(strToHash):
    salt = bcrypt.gensalt(5)
    return bcrypt.hashpw(strToHash.encode('utf-8'), salt)

def checkPw(clearPw, hashedPw):
    return bcrypt.checkpw(clearPw.encode('utf-8'), hashedPw)
