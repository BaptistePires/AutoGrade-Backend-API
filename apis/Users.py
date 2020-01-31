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
from core.Utils.Exceptions.ConnectDatabaseError import ConnectDatabaseError
from core.Utils.DatabaseFunctions.UsersFunctions import *
from core.Utils.DatabaseFunctions.GroupsFunctions import *
from itsdangerous import BadSignature, SignatureExpired
from bson import json_util
from core.Utils.Constants.ApiModels import *
# Dev imports
from time import sleep

##############
# API Object #
##############

api = Namespace('users', description="Users related operations.")
##############
# API models #
##############

userEval = api.model('UserEvaluator', {
    NAME_FIELD: fields.String('Name of the user.'),
    LASTNAME_FIELD: fields.String('Lastname of the user.'),
    MAIL_FIELD: fields.String('Mail of the user.'),
    PASSWORD_FIELD: fields.String('Password of the user.'),
    ORGANISATION_FIELD: fields.String('Organisation of the user.')
})
userCandidate = api.model('UserCandidate', {'name': fields.String('Name of the user.'),
                                            'lastname': fields.String('Lastname of the user.'),
                                            'email': fields.String('Mail of the user.'),
                                            "organisation": fields.String('Organisation of the user.'),
                                            })

loginModel = api.model('LoginModel', {
    MAIL_FIELD: fields.String('Mail of the user'),
    PASSWORD_FIELD: fields.String('Password of the user.')
})
userModel = api.model('UserModel', {
    NAME_FIELD: fields.String(),
    LASTNAME_FIELD: fields.String,
    MAIL_FIELD: fields.String(),
    PASSWORD_FIELD: fields.String(),
})

addOneCandModel = api.model('addOneCand', {
    'mail_candidate': fields.String('Candidate email'),
    'group_name': fields.String('Name of the group the candidate has to be added.')
})
addManyCandModel = api.model('addManyCand', {
    'mail_eval': fields.String(),
    'mailList': fields.List(fields.String),
    'group_name': fields.String()
})

candidateRegisterModel = api.model('Candidate register and validate route', {
    NAME_FIELD: fields.String('Candidate name'),
    LASTNAME_FIELD: fields.String('Candidate lastname'),
    PASSWORD_FIELD: fields.String('Candidate password'),
    MAIL_FIELD: fields.String(
        'Candidate mail address - This should be provided in the mail sent when an evaluator add him.'),
    ORGANISATION_FIELD: fields.String('Organisation of the candidate, can be null')
})

###########################
#  API responses models   #
###########################
USER_GET_INFO_MODEL = api.model('Get info sample', {
    NAME_FIELD: fields.String('Name of the current user'),
    LASTNAME_FIELD: fields.String('Lastname of the current user'),
    MAIL_FIELD: fields.String('Mail of the current user'),
    TYPE_FIELD: fields.String('Type of the user, either Evaluator or Candidate'),
    'groups': fields.List(fields.String('Name of the groups'))
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

@api.route('/authenticate')
class UserLogin(Resource):

    GET_FIELDS = (MAIL_FIELD, PASSWORD_FIELD)

    @api.expect(loginModel)
    @api.doc(responses={
        200: str({"status": 0, "auth_token": 'token'}),
        404: 'User does not exist or wrong mail/password.',
        401: 'Accoutn not confirmed',
        422: str(UNPROCESSABLE_ENTITY_RESPONSE[0]),
        503: str(DATABASE_QUERY_ERROR[0])
    })
    def post(self):
        """
            This route allow a user to have an API KEY that will allows him to do request.
        """
        if not all(x in api.payload for x in
                   self.GET_FIELDS) or len(api.payload) != len(self.GET_FIELDS): return UNPROCESSABLE_ENTITY_RESPONSE
        try:
            userInDb = db.getOneUserByMail(api.payload["email"])
            if userInDb is None:
                return UNKNOWN_USER_RESPONSE
            else:
                if not checkPw(api.payload["password"], userInDb['password']): return MAIL_OR_PASS_ERR
                if userInDb[CONFIRMED_FIELD] is False:
                    return MAIL_NOT_CONFIRMED
                else:
                    token = encodeAuthToken(userInDb['email'])
                    return {"status": 0, "auth_token": token}
        except ConnectDatabaseError:
            return DATABASE_QUERY_ERROR


@api.route('/get/info')
class GetUserInfo(Resource):

    @token_requiered
    @api.doc(security='apikey', responses={
        200: 'Query went ok, response in the \'user_data\' tag.',
        404: 'Unknow user',
        503: 'Database query error'
    })
    def get(self):
        """
            This route allow current user to retrieve his data, Evaluators and candidates can call this route.
        """
        mail = decodeAuthToken(request.headers['X-API-KEY'])
        try:
            user = getOneUserByMail(mail)
            if user is None: return UNKNOWN_USER_RESPONSE
            responseData = parseUserInfoToDict(user)
            return {'status': 0, 'user_data': responseData.copy()}, 200
        except ConnectDatabaseError:
            return DATABASE_QUERY_ERROR


@api.route('/delete')
class DeleteCurrentUser(Resource):

    @api.doc(security='apikey', responses={
        200: 'User deleted.',
        401: 'Wrong user type, this route should be called by a candidate',
        503: 'Error while connecting to the database'
    })
    def delete(self):
        """
            Delete by a candidate to delete his current account. - Not fully implemented.
        """
        mail = decodeAuthToken(request.headers['X-API-KEY'])
        try:
            user = getOneUserByMail(mail)
            if user[TYPE_FIELD] == CANDIDATE_TYPE:
                candidate = getCandidateByUserId(user['_id'])
                deleteCandidateProcedure(user, candidate)
            else:
                return WRONG_USER_TYPE
        except ConnectDatabaseError:
            return DATABASE_QUERY_ERROR


###########################
# Evaluators users routes #
###########################

@api.route('/evaluator/confirmation/<string:token>')
@api.doc(params={'token': 'Token received within confirmation mail.'})
class userConfirmation(Resource):

    @api.doc(responses={401: 'Token expired or invalid',
                        404: 'Unknow user'})
    def put(self, token):
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
                return UNKNOWN_USER_RESPONSE
            return BASIC_SUCCESS_RESPONSE
        except  SignatureExpired as e:
            return CONF_TOKEN_SIGN_EXPIRED
        except  BadSignature as e:
            return CONF_TOKEN_BAD_SIGNATURE
        except ConnectDatabaseError:
            return DATABASE_QUERY_ERROR


@api.route('/evaluator/register')
class EvalRegister(Resource):

    POST_FIELDS = (NAME_FIELD, LASTNAME_FIELD, MAIL_FIELD, ORGANISATION_FIELD, PASSWORD_FIELD)
    @api.expect(userEval, validate=True)
    @api.doc(responses={
        200: str({'status': 0, 'confirm_token': 'token'}),
        409: str(MAIL_NOT_AVAILABLE[0]),
        400: str(WRONG_MAIL_FORMAT[0]) + ' or ' + str(PASSWORD_NOT_STRONG_ENOUGH[0]),
        422: str(UNPROCESSABLE_ENTITY_RESPONSE[0]),
        503: str(DATABASE_QUERY_ERROR[0])
    })
    def post(self):
        """
            Register as an evaluator.
        """
        if not all(x in api.payload for x in
                   self.POST_FIELDS) or len(self.POST_FIELDS) != len(api.payload): return UNPROCESSABLE_ENTITY_RESPONSE
        try:
            if api.payload[MAIL_FIELD] in db.getAllUsersMail(): return MAIL_NOT_AVAILABLE
            if not checkEmailFormat(api.payload[MAIL_FIELD]): return WRONG_MAIL_FORMAT
            if not validatePassword(api.payload[PASSWORD_FIELD]): return PASSWORD_NOT_STRONG_ENOUGH
            user = setupUserDictFromHTTPPayload(api.payload, EVALUATOR_TYPE)
            idUser = db.insert(USERS_DOCUMENT, user.copy())
            token = generateMailConfToken(user[MAIL_FIELD])
            eval = EVALUATORS_ITEM_TEMPLATE
            eval[USER_ID_FIELD] = idUser.inserted_id
            eval[ORGANISATION_FIELD] = api.payload[ORGANISATION_FIELD]
            db.insert(EVALUATORS_DOCUMENT, eval.copy())
            import sys
            if not sys.platform.startswith('darwin'):
                MailHandler.sendPlainTextMail(user[MAIL_FIELD], "Inscription à AutoGrade !",
                                              CONTENT_MAIL_CONF.format(token=token))
            return {'status': 0, 'confirm_token': token}
        except ConnectDatabaseError:
            return DATABASE_QUERY_ERROR


@api.route('/evaluator/add/candidate')
class EvalAddCand(Resource):

    POST_FIELDS = (apiModels.CANDIDATE_MAIL, apiModels.GROUP_NAME)

    @token_requiered
    @api.expect(addOneCandModel)
    @api.doc(security='apikey', responses={200: str(CANDIDATE_ADDED_RESPONSE[
                                                        0]) + ' or ' + '{\'status\': 0, \'info\': \'Ajout et envoi du mail terminé.\', \'confirm_token\': validationToken}',
                                           401: str(TOKEN_EXPIRED[0]) + ' or ' + str(INVALID_TOKEN[0]),
                                           403: 'This user already exists and is a evaluator.',
                                           404: 'Group does not exist.',
                                           409: 'User already in group.',
                                           422: str(UNPROCESSABLE_ENTITY_RESPONSE[0])
                                           })
    def post(self):
        """
            This method add a candidate to a group. If the mail is not alreayd in the database, it will create a user
            and a candidate entity and add it to the group. If the user is already taken, it will check if the user
            is a cancidate, if not it'll return an 403 response. If it's a candidate, then ii'll add it to the group.
        """
        if not all(x in api.payload for x in
                   self.POST_FIELDS) or len(self.POST_FIELDS) != len(api.payload): return UNPROCESSABLE_ENTITY_RESPONSE
        mail = decodeAuthToken(request.headers['X-API-KEY'])
        try:
            evaluator = getEvalFromMail(mail)
            user = getOneUserByMail(api.payload[apiModels.CANDIDATE_MAIL])
            group = getEvalGroupFromName(evaluator['_id'], api.payload[apiModels.GROUP_NAME])
            cand = None
            if user is not None:
                if user[TYPE_FIELD] == EVALUATOR_TYPE:
                    return {'status': -1,
                            'error': 'User already exists and is an evaluator, you can\'t add evaluators in a group.'}
                else:
                    cand = getCandidateByUserId(str(user['_id']))
                    for grp in cand[CANDIDATES_GROUPS_FIELD]:
                        if getGroupFromId(str(grp))[GROUPS_NAME_FIELD] == api.payload[apiModels.GROUP_NAME]:
                            return USER_ALREADY_IN_GROUP
                    addGroupToCandidate(str(cand['_id']), str(group['_id']))
                    return CANDIDATE_ADDED_RESPONSE

            else:
                user = addCandidate(api.payload[apiModels.CANDIDATE_MAIL], str(group['_id']))
                validationToken = generateMailConfToken(api.payload[apiModels.CANDIDATE_MAIL])
                evalUser = getUserById(evaluator[USER_ID_FIELD])
                txtMail = "Hello,\n {name} {lastname} invites you to join his group to .... click the link below to validate your account. link here : token : {mail} :::: {token}".format(
                    name=evalUser[NAME_FIELD], lastname=evalUser[LASTNAME_FIELD], token=validationToken,
                    mail=api.payload[apiModels.CANDIDATE_MAIL])
                MailHandler.sendPlainTextMail(api.payload[apiModels.CANDIDATE_MAIL],
                                              "Vous êtes invité à rejoindre AutoGrade !", txtMail)
                return {'status': 0, 'info': 'Ajout et envoi du mail terminé.', 'confirm_token': validationToken}, 200
        except ConnectDatabaseError as e:
            return DATABASE_QUERY_ERROR
        except WrongUserTypeException:
            return WRONG_USER_TYPE
        except GroupDoesNotExistException:
            return GROUP_DOES_NOT_EXIST


@api.route('/Eval/<string:userId>/AddManyCand', doc=False)
class EvalAddManyCand(Resource):

    @token_requiered
    @api.expect(addManyCandModel)
    def post(self, userId):
        """
            Not implemented yet.
        :param userId:
        :return:
        """
        # TODO : Call @api.route('/Eval/<string:userId>/AddOneCand/<string:mail>') to add all mails.
        return {"maillist": api.payload["mailList"]}


###########################
# Candidates users routes #
###########################

@api.route('/candidate/confirmation/<string:token>')
class CandidatesRegisterHandler(Resource):
    """
        This route allows you to confirm a candidate account by providing all the information needed.
        The token is valid 48h.
    """

    PUT_FIELDS = (NAME_FIELD, LASTNAME_FIELD, ORGANISATION_FIELD, MAIL_FIELD, PASSWORD_FIELD)
    @api.expect(candidateRegisterModel, validate=True)
    @api.doc(responses={200: 'User registred.',
                        401: 'Token has a bad signature or has expired',
                        404: 'Unknow candidate',
                        422: str(UNPROCESSABLE_ENTITY_RESPONSE[0]),
                        503: 'Databse error'})
    def put(self, token):
        """
            Register as a candidate after that the evaluator added the candidate.
        """
        if not all(x in api.payload for x in self.PUT_FIELDS) or \
                len(self.PUT_FIELDS) != len(api.payload): return UNPROCESSABLE_ENTITY_RESPONSE
        try:
            mail = validateConfToken(token)
            if mail is None: return UNKNOWN_USER_RESPONSE
            mailPayload = api.payload[MAIL_FIELD].lower()
            if mail != mailPayload: return MAIL_NOT_MATCHING_TOKEN
            user = getOneUserByMail(mail)
            if user is None: return UNKNOWN_USER_RESPONSE
            if user[TYPE_FIELD] != CANDIDATE_TYPE: return WRONG_USER_TYPE
            if user[CONFIRMED_FIELD]: return MAIL_ADDR_ALREADY_CONFIRMED
            candidate = getCandidateByUserId(user['_id'])
            user = setUpUserDictForRegisterCandidate(user, api.payload)
            createFolderForUserId(user['_id'])
            candidate[ORGANISATION_FIELD] = api.payload[ORGANISATION_FIELD]
            if registerCandidate(candidate=candidate, user=user):
                return BASIC_SUCCESS_RESPONSE
            else:
                return DATABASE_QUERY_ERROR
        except ConnectDatabaseError:
            return DATABASE_QUERY_ERROR
        except  SignatureExpired as e:
            return CONF_TOKEN_SIGN_EXPIRED
        except  BadSignature as e:
            return CONF_TOKEN_BAD_SIGNATURE

updateUserModel = api.model('Update user model', {
    NAME_FIELD: fields.String('New '+ NAME_FIELD+'of the user, null if there is no update', allow_null=True),
    LASTNAME_FIELD: fields.String('New '+ LASTNAME_FIELD+'of the user, null if there is no update', allow_null=True),
    ORGANISATION_FIELD: fields.String('New '+ ORGANISATION_FIELD +'of the user, null if there is no update', allow_null=True)
})

@api.route('/update')
class UpdateUser(Resource):

    @api.expect(updateUserModel)
    @token_requiered
    @api.doc(security='apikey', responses={
        200: 'Query went OK',
        404: str(UNKNOWN_USER_RESPONSE[0]),
        422: str(UNPROCESSABLE_ENTITY_RESPONSE[0]),
        503: str(DATABASE_QUERY_ERROR[0])
    })
    def put(self):
        """
             Update those fields for a user, If there is no changes, you have to let them empty, otherwise it will
             be updated.
             Evaluators and candidates can call it.
        """
        if len(api.payload) < 1:return UNPROCESSABLE_ENTITY_RESPONSE
        mail = decodeAuthToken(request.headers['X-API-KEY'])
        try:
            user = getOneUserByMail(mail)
            if user is None: return UNKNOWN_USER_RESPONSE
            fieldsToUpdate = {}
            for field in api.payload:
                if field in [NAME_FIELD, LASTNAME_FIELD, ORGANISATION_FIELD]:
                    if len(api.payload[field]) > 0:fieldsToUpdate[field] = api.payload[field]
            result = updateUserFields(user['_id'], fieldsToUpdate)
            return BASIC_SUCCESS_RESPONSE
        except ConnectDatabaseError:
            return DATABASE_QUERY_ERROR
