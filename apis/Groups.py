from flask_restplus import Namespace, Resource, fields, marshal_with
from core.Utils.Exceptions.ExpiredTokenException import ExpiredTokenException
from core.Utils.Exceptions.InvalidTokenException import InvalidTokenException
from core.Utils.Exceptions.ConnectDatabaseError import ConnectDatabaseError
from core.Utils.Exceptions.GroupDoesNotExistException import GroupDoesNotExistException
from core.Utils.Constants.ApiResponses import *
from pymongo import errors
from datetime import datetime
from core.Utils.Utils import *
from flask import request
from core.Utils.DatabaseFunctions.UsersFunctions import *
from core.Utils.DatabaseFunctions.GroupsFunctions import *
from core.Utils.Utils import isDateBeforeNow
from core.Utils.DatabaseFunctions.AssignmentsFunctions import getAssignmentFromId
from bson.json_util import dumps

# TODO : Add try/ Catch for connection refused to db
api = Namespace('groups', description="Groups related operations.")

groupModel = api.model('group', {
    'name': fields.String('Group\' name.')
})

addUserModel = api.model('addUserToGroupModel', {
    'name': fields.String('Group\' name.'),
    'user_mail': fields.String('Mail address of the user')
})


@api.route('/create')
class CreateGroup(Resource):

    @api.expect(groupModel)
    @token_requiered
    @api.doc(security='apikey')
    def post(self):
        try:
            mail = decodeAuthToken(request.headers['X-API-KEY'])
            eval = getEvalFromMail(mail.lower())
            if eval is None: return UNKNOW_USER_RESPONSE
            if api.payload[GROUPS_NAME_FIELD] in getAllGroupNameFromEvalId(
                eval['_id']): return GROUP_NAME_ALREADY_EXISTS
            group = GROUP_TEMPLATE
            group[GROUPS_ID_EVAL_FIELD] = eval['_id']
            group[GROUPS_NAME_FIELD] = api.payload[GROUPS_NAME_FIELD]
            group[CREATED_TIMESTAMP] = str(datetime.now())
            result = db.insert(GROUPS_DOCUMENT, group.copy())
            db.addGroupToUser(eval['_id'], result.inserted_id)
            addGroupToEval(eval['_id'], result.inserted_id)
            createFolderForGroup(result.inserted_id)
            return BASIC_SUCCESS_RESPONSE
        except ExpiredTokenException:
            return TOKEN_EXPIRED, 401
        except InvalidTokenException:
            return MAIL_NOT_MATCHING_TOKEN, 401
        except ConnectDatabaseError:
            return DATABASE_QUERY_ERROR

@api.route('/get/evaluator/all')
class GetAllGroups(Resource):

    @token_requiered
    @api.doc(security='apikey', responses={
        200: 'User data in the body',
        503: 'Error while connecting to the database'
    })
    def get(self):
        """
            Retrieve current user data.
        :return:
        """
        try:
            mail = decodeAuthToken(request.headers['X-API-KEY'])
            groups = getAllEvalGroups(mail)
            output = formatGroupsForEval(groups)
            return {'status': 0, 'groups': output}
        except ConnectDatabaseError:
            return DATABASE_QUERY_ERROR


@api.route('/add/candidate')
class addUserToGroup(Resource):

    @token_requiered
    @api.expect(addUserModel)
    @api.doc(security='apikey')
    def post(self):
        # TODO : Check if candidate exists or not
        try:
            mail = decodeAuthToken(request.headers['X-API-KEY'])
            eval = getEvalFromMail(mail)
            if eval is None: return UNKNOW_USER_RESPONSE
            group = db.getGroupByEvalIdAndName(eval['_id'], api.payload['name'].lower())
            user = db.getOneUserByMail(mail)
            if user is None: return UNKNOW_USER_RESPONSE
            uAdd = db.addGroupToUser(user['_id'], group['_id'])
            gAdd = db.addUserToGroup(group['_id'], user['_id'])
            if uAdd is not None and gAdd is not None:
                return {"status": 0}
            else:
                return {'stauts': -1, 'error': 'Il y a eu une erreur lors de l\'ajout au groupe.'}
        except ConnectDatabaseError:
            return DATABASE_QUERY_ERROR


addAssignmentToGoupModel = api.model('Add assignment to group model', {
    'group_name': fields.String('Name of the group'),
    'assignID': fields.String('Id of the assignment, this ID can be retrieved with assignments routes.'),
    'deadline': fields.String('Deadline of this assignment, format MUST be : YYYY/MM/dd %H:%M:%S')
})


@api.route('/assignment/add')
class addAssignmentToGroup(Resource):

    @api.doc(security='apikey')
    @token_requiered
    @api.expect(addAssignmentToGoupModel)
    def post(self):
        try:
            eval = getEvalFromMail(decodeAuthToken(request.headers['X-API-KEY']))
            if eval is None: return UNKNOW_USER_RESPONSE
            groups = getAllGroupsFromUserId(eval['_id'])
            if api.payload['group_name'] not in [g[GROUPS_NAME_FIELD] for g in groups]: return GROUP_DOES_NOT_EXIST
            group = None
            for g in groups:
                if g[GROUPS_NAME_FIELD] == api.payload['group_name']:
                    group = g
            assign = getAssignmentFromId(api.payload['assignID'])
            if assign is None: return ASSIGNMENT_DOES_NOT_EXIST
            if assign['_id'] in [x[GROUPS_ASSIGNMENTS_IDS_FIELD] for x in
                                 group[GROUPS_ASSIGNMENTS_FIELD]]: return ASSIGNMENT_ALREADY_ASSIGNED_TO_GROUP
            deadline = datetime.strptime(api.payload['deadline'], '%Y/%m/%d %H:%M:%S')
            if isDateBeforeNow(deadline): return DATE_BEFORE_NOW
            addAssignToGroup(groupId=group['_id'], assignId=assign['_id'], deadline=deadline)
            createFolderAssignmentForGroup(group['_id'], assign['_id'])
            return BASIC_SUCCESS_RESPONSE
        except ConnectDatabaseError:
            return DATABASE_QUERY_ERROR
        except GroupDoesNotExistException:
            return GROUP_DOES_NOT_EXIST

@api.route('/get/candidate/all')
class CandidateGetAllGroups(Resource):

    @token_requiered
    @api.doc(security='apikey', responses={
        200: 'Groups in the "groups" field"',
        401: 'Token invalid or expired',
        503: 'Error with the database'
    })
    def get(self):
        mail = decodeAuthToken(request.headers['X-API-KEY'])
        try:
            candidate = getCandidateFromMail(mail)
            groups = getAllCandidateGroups(candidate)
            return {'status': 0, 'groups': groups}
        except ConnectDatabaseError:
            return DATABASE_QUERY_ERROR
        except GroupDoesNotExistException:
            return GROUP_DOES_NOT_EXIST

@api.route('/get/candidate/one/<string:group_id>')
class CandidateGetOneGroup(Resource):

    @token_requiered
    @api.doc(security='apikey', responses={
        200: 'Query went OK, group data in object \'group\'.',
        401: 'Invalid or expired token.',
        403: 'Wrong user type, this route require candidate user.',
        404: 'Group does not exist or the evaluator that created the group does not exist anymore too.',
        503: 'Error with the database.'
    })
    def get(self, group_id):
        mail = decodeAuthToken(request.headers['X-API-KEY'])
        try:
            candidate = getCandidateFromMail(mail)
            group = getGroupFromId(group_id)
            if group is None: return GROUP_DOES_NOT_EXIST
            formatedGroup = formatGroupForCandidate(group, candidate['_id'])
            return {'status': 0, 'group': formatedGroup}
        except ConnectDatabaseError:
            return DATABASE_QUERY_ERROR
        except WrongUserTypeException:
            return WRONG_USER_TYPE
        except EvaluatorDoesNotExist:
            return GROUP_DOES_NOT_EXIST

@api.route('/get/evaluator/one/<string:group_id>')
class EvaluatorGetOneGroup(Resource):

    @token_requiered
    @api.doc(security='apikey', responses= {
        200: 'Query went OK, group data in object \'group\'.',
        404: 'This user of type evaluator does not exist or the group does not exist or the current user does not own'
             'the group.',
        503: 'Error with the database.'
    })
    def get(self, group_id):
        mail = decodeAuthToken(request.headers['X-API-KEY'])
        try:
            evaluator = getEvalFromMail(mail)
            if evaluator is None: return UNKNOW_USER_RESPONSE
            group = getGroupFromId(group_id)
            if group is None: return GROUP_DOES_NOT_EXIST
            if group[GROUPS_ID_EVAL_FIELD] != evaluator['_id']: return GROUP_DOES_NOT_EXIST
            formatedGroup = formatGroupForEval(group, evaluator['_id'])
            return {'status':0, 'group': formatedGroup}
        except PyMongoError:
            return DATABASE_QUERY_ERROR

