from flask_restplus import Namespace, Resource, fields
from core.Utils.Constants.DatabaseConstants import *
import core.Utils.Constants.ApiModels as apiModels
from core.Utils.Constants.ErrorsStringConstants import *
from core.Utils.Constants.UtilsStringConstants import CONTENT_MAIL_CONF
from core.Utils.Constants.ApiResponses import *
from core.Utils.DatabaseHandler import DatabaseHandler
from core.Utils.Utils import *
from core.Utils.MailHandler import MailHandler
from flask import request
from core.Utils.Exceptions.WrongUserTypeException import WrongUserTypeException
from core.Utils.Exceptions.GroupDoesNotExistException import GroupDoesNotExistException
from core.Utils.DatabaseFunctions.UsersFunctions import *
from core.Utils.DatabaseFunctions.GroupsFunctions import *
from itsdangerous import BadSignature, SignatureExpired
# Dev imports
from time import sleep

##############
# API Object #
##############

api = Namespace('users', description="Users related operations.")
##############
# API models #
##############

userEval = api.model('UserEvaluator', {'name': fields.String('Name of the user.'),
                            'lastname': fields.String('Lastname of the user.'),
                            'email': fields.String('Mail of the user.'),
                            'password': fields.String('Password of the user.'),
                            "organisation": fields.String('Organisation of the user.')
                              })

userCandidate = api.model('UserCandidate', {'name': fields.String('Name of the user.'),
                                'lastname': fields.String('Lastname of the user.'),
                                'email': fields.String('Mail of the user.'),
                                "organisation": fields.String('Organisation of the user.'),
                              })

userModel = api.model('UserModel', {
    'name': fields.String(),
    'lastname': fields.String,
    'email': fields.String(),
    'password': fields.String(),
})

addOneCandModel = api.model('addOneCand', {
    'mail_eval' : fields.String('Evaluator mail'),
    'mail_candidate': fields.String('Candidate email'),
    'group_name': fields.String('Name of the group the candidate has to be added.')
})
addManyCandModel = api.model('addManyCand', {
    'mail_eval': fields.String(),
    'mailList': fields.List(fields.String),
    'group_name' : fields.String()
})

candidateRegisterModel = api.model('Candidate register and validate route', {
    NAME_FIELD: fields.String('Candidate name'),
    LASTNAME_FIELD: fields.String('Candidate lastname'),
    PASSWORD_FIELD: fields.String('Candidate password'),
    MAIL_FIELD: fields.String('Candidate mail address - This should be provided in the mail sent when an evaluator add him.'),
    ORGANISATION_FIELD: fields.String('Organisation of the candidate, can be null')
})

###################
# Database Object #
###################

db = DatabaseHandler()
db.connect()

###########
# Routes #
###########

#######################
# Global users routes #
#######################

@api.route('/', doc=False)
class Users(Resource):

    def get(self):
        items = db.getCollectionItems(USERS_DOCUMENT)
        for i in items:
            i["_id"] = str(i['_id'])
            i["password"] = i["password"].decode('utf-8')
        return {"users": items}


@api.route('/ClearDb')
class ClearDb(Resource):

    def get(self):
        db.clearDocument(USERS_DOCUMENT)
        db.clearDocument("evaluators")
        
@api.route('/Authenticate')
class UserLogin(Resource):

    @api.expect(userModel)
    @api.doc(responses={404: 'User does not exist.', 404: 'Wrong mail or password or unknow user.', 401: 'Accoutn not confirmed'})
    def post(self):
        """
            This route allow a user to have an API KEY that will allows him to do request.
        :return:
        """
        userInDb = db.getOneUserByMail(api.payload["email"])
        if userInDb is None: return UNKNOW_USER_RESPONSE
        else:
            if not checkPw(api.payload["password"], userInDb['password']):return MAIL_OR_PASS_ERR
            if userInDb['confirmed'] is False: return MAIL_NOT_CONFIRMED
            else:
                token = encodeAuthToken(userInDb['email'])
                return {"status": 0, "auth_token": token}


###########################
# Evaluators users routes #
###########################
@api.route('/Eval/Confirmation/<string:token>')
@api.doc(params={'token': 'Token received within confirmation mail.'})
class userConfirmation(Resource):

    @api.doc(responses={401: 'Token expired or invalid', 404: 'Unknow user'})
    def get(self, token):
        """
            This route allows you to confirm an evaluator account.
        """
        try:
            mail = validateConfToken(token)
            user = db.getOneUserByMail(mail)
            if user != None:
                if user["confirmed"]:
                    return MAIL_ADDR_ALREADY_CONFIRMED
                else:
                    db.updateConfirmationOfUserWithMail(mail)
            else:
                return UNKNOW_USER_RESPONSE
            return BASIC_SUCCESS_RESPONSE
        except  SignatureExpired as e:
            return CONF_TOKEN_SIGN_EXPIRED
        except  BadSignature as e:
            return CONF_TOKEN_BAD_SIGNATURE

@api.route('/Eval/ClearDb')
class ClearEvalDb(Resource):

    def get(self):
        db.clearDocument("evaluators")


@api.route('/Eval/Register')
class EvalRegister(Resource):

    @api.hide
    def get(self):
        items = db.getCollectionItems(EVALUATORS_DOCUMENT)
        for i in items:
            i["_id"] = str(i['_id'])
            i["user_id"] = str(i['user_id'])
        return {"users": items}

    @api.expect(userEval)
    @api.doc(responses={409: 'Mail address already used.', 400: 'Wrong mail format or any other error.'})
    def post(self):
        """
            Create a Evaluator User. Send mail de confirmation # TODO send mail
        :return:
        """
        try:
            if api.payload[MAIL_FIELD] in db.getAllUsersMail(): return MAIL_NOT_AVAILABLE
            if not checkEmailFormat(api.payload[MAIL_FIELD]): return WRONG_MAIL_FORMAT
            user = setupUserDictFromHTTPPayload(api.payload, EVALUATOR_TYPE)
            idUser = db.insert(USERS_DOCUMENT, user.copy())
            eval = EVALUATORS_ITEM_TEMPLATE
            eval[USER_ID_FIELD] = idUser.inserted_id
            eval[ORGANISATION_FIELD] = api.payload[ORGANISATION_FIELD]
            db.insert(EVALUATORS_DOCUMENT, eval.copy()  )
            createFolderForUserId(eval[USER_ID_FIELD])
            MailHandler.sendPlainTextMail(user[MAIL_FIELD], "Inscription à AutoGrade !", CONTENT_MAIL_CONF.format(token=generateMailConfToken(user["email"])))
            return BASIC_SUCCESS_RESPONSE
        except Exception as e:
            return BASIC_ERROR_RESPONSE


@api.route('/Eval/AddOneCand')
class EvalAddCand(Resource):

    @token_requiered
    @api.expect(addOneCandModel)
    @api.doc(security='apikey', responses={200: 'Candidate added', 422: 'Wrong format of data sent', 401: 'Token exprired or corrupted', 403: 'The user is a Candidate, only Evaluators can add candidates.', 404: 'Group does not exist.', 409: 'User already in group.'})
    def post(self):
        """
            This method add a candidate to a group. If the mail is not alreayd in the database, it will create a user
            and a candidate entity and add it to the group. If the user is already taken, it will check if the user
            is a cancidate, if not it'll return an 403 response. If it's a candidate, then ii'll add it to the group.
        """
        if not all(x in api.payload for x in (apiModels.EVALUATOR_MAIL, apiModels.CANDIDATE_MAIL, apiModels.GROUP_NAME)): return UNPROCESSABLE_ENTITY_RESPONSE
        try:
            if not validateToken(api.payload[apiModels.EVALUATOR_MAIL], request.headers['X-API-KEY']): return MAIL_NOT_MATCHING_TOKEN
            eval = getEvalFromMail(api.payload[apiModels.EVALUATOR_MAIL])
            group = getEvalGroupFromName(eval, api.payload[apiModels.GROUP_NAME])
            user = getOneUserByMail(api.payload[apiModels.CANDIDATE_MAIL])
            cand = None
            if user is not None:
                if user[TYPE_FIELD] == EVALUATOR_TYPE:
                    return {'status': -1, 'error': 'User already exists and is an evaluator, please use another mail for this user.'}
                else:
                    cand = getCandidateByUserId(str(user['_id']))
                    for grp in cand[CANDIDATES_GROUPS_FIELD]:
                        if getGroupFromId(str(grp))[GROUPS_NAME_FIELD] == api.payload[apiModels.GROUP_NAME]:
                            return USER_ALREADY_IN_GROUP
                    addGroupToCandidate(str(cand['_id']), str(group['_id']))
                    return {'status': 0, 'infos': 'Group added to the user.'}

            else:
                user = addCandidate(api.payload[apiModels.CANDIDATE_MAIL], str(group['_id']))
                validationToken = generateMailConfToken(api.payload[apiModels.CANDIDATE_MAIL])
                evalUser = getUserById(eval[USER_ID_FIELD])
                txtMail = "Hello,\n {name} {lastname} invites you to join his group to .... click the link below to validate your account. link here : token : {mail} :::: {token}".format(name=evalUser[NAME_FIELD], lastname=evalUser[LASTNAME_FIELD], token=validationToken, mail=api.payload[apiModels.CANDIDATE_MAIL])
                MailHandler.sendPlainTextMail(api.payload[apiModels.CANDIDATE_MAIL], "Vous êtes invité à rejoindre AutoGrade !", txtMail)
                return {'status': 0, 'info': 'Ajout et envoi du mail terminé.'}, 200

        except WrongUserTypeException:
            return WRONG_USER_TYPE
        except GroupDoesNotExistException:
            return GROUP_DOES_NOT_EXIST
        except ExpiredTokenException:
            return TOKEN_EXPIRED

@api.route('/Eval/<string:userId>/AddManyCand')
class EvalAddManyCand(Resource):

    @token_requiered
    @api.expect(addManyCandModel)
    def post(self, userId):
        # TODO : Call @api.route('/Eval/<string:userId>/AddOneCand/<string:mail>') to add all mails.
        return {"maillist": api.payload["mailList"]}

###########################
# Candidates users routes #
###########################

@api.route('/Candidate/Confirmation/<string:token>')
class CandidatesRegisterHandler(Resource):
    """
        This route allows you to confirm a candidate account by providing all the information needed.
        The token is valid 48h.
    """
    @api.expect(candidateRegisterModel)
    @api.doc(responses={401: 'Token has a bad signature or has expired', 200: 'User registred.', 503: 'Databse error', 404: 'Unknow candidate', 422: 'Data sent malformed.'})
    def post(self, token):
        if not all(x in api.payload for x in (NAME_FIELD, LASTNAME_FIELD, ORGANISATION_FIELD, MAIL_FIELD, PASSWORD_FIELD)): return UNPROCESSABLE_ENTITY_RESPONSE

        try:
            mail = validateConfToken(token)
            if mail is None: return UNKNOW_USER_RESPONSE
            if mail != api.payload[MAIL_FIELD]: return MAIL_NOT_MATCHING_TOKEN
            user = getOneUserByMail(mail)
            if user is None: return UNKNOW_USER_RESPONSE
            if user[TYPE_FIELD] != CANDIDATE_TYPE: return WRONG_USER_TYPE
            if user[CONFIRMED_FIELD]: return MAIL_ADDR_ALREADY_CONFIRMED
            candidate = getCandidateByUserId(user['_id'])
            user = setUpUserDictForRegisterCandidate(user, api.payload)
            candidate[ORGANISATION_FIELD] = api.payload[ORGANISATION_FIELD]
            if registerCandidate(candidate=candidate, user=user):
                return BASIC_SUCCESS_RESPONSE
            else:
                return DATABASE_QUERY_ERROR
        except  SignatureExpired as e:
            return CONF_TOKEN_SIGN_EXPIRED
        except  BadSignature as e:
            return CONF_TOKEN_BAD_SIGNATURE