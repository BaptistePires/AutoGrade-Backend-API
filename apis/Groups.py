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
from core.Utils.Utils import isTimestampBeforeNow
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

    POST_FIELDS = [x for x in groupModel]

    @api.expect(groupModel)
    @token_requiered
    @api.doc(security='apikey', responses={
        200: 'Query went OK, the group has been created.',
        401: 'The token is invalid or expired',
        403: 'The current evaluator has already a grouped called with the same name.',
        404: 'Unknown user.',
        422: str(UNPROCESSABLE_ENTITY_RESPONSE[0]),
        503: 'Database query error.'
    })
    def post(self):
        """
            Create a group as an evaluator.
            This route can only be called by an evaluator.
        """
        if not all(x in api.payload for x in self.POST_FIELDS) or \
                len(self.POST_FIELDS) != len(api.payload): return UNPROCESSABLE_ENTITY_RESPONSE
        try:
            mail = decodeAuthToken(request.headers['X-API-KEY'])
            eval = getEvalFromMail(mail.lower())
            if eval is None: return UNKNOWN_USER_RESPONSE
            if api.payload[GROUPS_NAME_FIELD] in getAllGroupNameFromEvalId(
                    eval['_id']): return GROUP_NAME_ALREADY_EXISTS
            group = GROUP_TEMPLATE
            group[GROUPS_ID_EVAL_FIELD] = eval['_id']
            group[GROUPS_NAME_FIELD] = api.payload[GROUPS_NAME_FIELD]
            group[CREATED_TIMESTAMP] = datetime.now().timestamp()
            result = db.insert(GROUPS_DOCUMENT, group.copy())
            db.addGroupToUser(eval['_id'], result.inserted_id)
            addGroupToEval(eval['_id'], result.inserted_id)
            createFolderForGroup(result.inserted_id)
            return BASIC_SUCCESS_RESPONSE
        except ConnectDatabaseError:
            return DATABASE_QUERY_ERROR


@api.route('/get/evaluator/all')
class GetAllGroups(Resource):

    @token_requiered
    @api.doc(security='apikey', responses={
        200: 'User data in the body',
        401: 'Token expired or invalid',
        404: 'Unknown user.',
        503: 'Error while connecting to the database'
    })
    def get(self):
        """
            Get all groups of the current evaluator.
            This route return
        :return:
        """
        try:
            mail = decodeAuthToken(request.headers['X-API-KEY'])
            evaluator = getEvalFromMail(mail)
            if evaluator is None: return UNKNOWN_USER_RESPONSE
            groups = getAllEvalGroups(evaluator['_id'])

            output = formatGroupsForEval(groups)
            return {'status': 0, 'groups': output}
        except ConnectDatabaseError:
            return DATABASE_QUERY_ERROR


@api.route('/add/candidate')
class addUserToGroup(Resource):

    PUT_FIELDS = [field for field in addUserModel]

    @token_requiered
    @api.expect(addUserModel)
    @api.doc(security='apikey', responses={
        200: str(BASIC_SUCCESS_RESPONSE[0]),
        404: str({'status': -1, 'error': 'Il y a eu une erreur lors de l\'ajout au groupe.'}) + ' or ' + str(UNKNOWN_USER_RESPONSE[0]),
        422: str(UNPROCESSABLE_ENTITY_RESPONSE[0]),
        503: str(DATABASE_QUERY_ERROR[0])
    })
    def put(self):
        """
            Add a candidate to a group as an evaluator.
            This group can only be called by an evaluator.
        """
        if not all(x in api.payload for x in self.PUT_FIELDS) or \
                len(self.PUT_FIELDS) != len(api.payload): return UNPROCESSABLE_ENTITY_RESPONSE
        # TODO : Check if candidate exists or not
        try:
            mail = decodeAuthToken(request.headers['X-API-KEY'])
            eval = getEvalFromMail(mail)
            if eval is None: return UNKNOWN_USER_RESPONSE
            group = db.getGroupByEvalIdAndName(eval['_id'], api.payload['name'].lower())
            user = db.getOneUserByMail(mail)
            if user is None: return UNKNOWN_USER_RESPONSE
            uAdd = db.addGroupToUser(user['_id'], group['_id'])
            gAdd = db.addUserToGroup(group['_id'], user['_id'])
            if uAdd is not None and gAdd is not None:
                return {"status": 0}
            else:
                return {'status': -1, 'error': 'Il y a eu une erreur lors de l\'ajout au groupe.'}, 404
        except ConnectDatabaseError:
            return DATABASE_QUERY_ERROR



addAssignmentToGoupModel = api.model('Add assignment to group model', {
    'group_name': fields.String('Name of the group'),
    'assignID': fields.String('Id of the assignment, this ID can be retrieved with assignments routes.'),
    'deadline': fields.Float('Deadline of this assignment, format MUST be a timestamp.')
})


@api.route('/add/assignment')
class addAssignmentToGroup(Resource):

    PUT_FIELDS = [field for field in addAssignmentToGoupModel]

    @token_requiered
    @api.expect(addAssignmentToGoupModel)
    @api.doc(security='apikey', responses={
        200: str(BASIC_SUCCESS_RESPONSE[0]),
        403: str(ASSIGNMENT_ALREADY_ASSIGNED_TO_GROUP[0]) + ' or ' + str(DATE_BEFORE_NOW[0]) + ' or ' + str(WRONG_USER_TYPE[0]),
        404: str(UNKNOWN_USER_RESPONSE[0]) + ' or ' + str(GROUP_DOES_NOT_EXIST[0]),
        422: str(UNPROCESSABLE_ENTITY_RESPONSE[0]),
        503: str(DATABASE_QUERY_ERROR[0])
    })
    def put(self):
        """
            Add assignment to a group as evaluator.
            This route can only be called by a evaluator to add a group to one of HIS groups.
        """
        if not all(x in api.payload for x in self.PUT_FIELDS) or \
                len(self.PUT_FIELDS) != len(api.payload): return UNPROCESSABLE_ENTITY_RESPONSE
        try:
            eval = getEvalFromMail(decodeAuthToken(request.headers['X-API-KEY']))
            if eval is None: return UNKNOWN_USER_RESPONSE
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
            if isTimestampBeforeNow(api.payload[ASSIGNMENT_DEADLINE]): return DATE_BEFORE_NOW
            addAssignToGroup(groupId=group['_id'], assignId=assign['_id'], deadline=api.payload[ASSIGNMENT_DEADLINE])
            createFolderAssignmentForGroup(group['_id'], assign['_id'])
            return BASIC_SUCCESS_RESPONSE
        except ConnectDatabaseError:
            return DATABASE_QUERY_ERROR
        except GroupDoesNotExistException:
            return GROUP_DOES_NOT_EXIST
        except WrongUserTypeException:
            return WRONG_USER_TYPE
        except TypeError:
            return {'status' : -1, 'error': 'Date must me a timestamp'}


@api.route('/get/candidate/all')
class CandidateGetAllGroups(Resource):

    @token_requiered
    @api.doc(security='apikey', responses={
        200: 'Groups in the "groups" field"',
        401: 'Token invalid or expired',
        503: 'Error with the database'
    })
    def get(self):
        """
            Route to get all the current candidate groups.
            This route return an array of {'id': idGroup, 'name': groupName} objects.
        :return:
        """
        mail = decodeAuthToken(request.headers['X-API-KEY'])
        try:
            candidate = getCandidateFromMail(mail)
            groups = getAllCandidateGroups(candidate)
            return {'status': 0, 'groups': groups}
        except ConnectDatabaseError:
            return DATABASE_QUERY_ERROR
        except GroupDoesNotExistException:
            return GROUP_DOES_NOT_EXIST
        except WrongUserTypeException:
            return WRONG_USER_TYPE


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
        """
            Get all group info for a the group_id of the candidate (only the data that a candidate is allowed to see).
            This route can only be called by a candidate.
        """
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
    @api.doc(security='apikey', responses={
        200: 'Query went OK, group data in object \'group\'.',
        404: 'This user of type evaluator does not exist or the group does not exist or the current user does not own'
             'the group.',
        503: 'Error with the database.'
    })
    def get(self, group_id):
        """
            Get all data of a group with the id group_id for an evaluator.
            This route can only be called by an evaluator.
        """
        mail = decodeAuthToken(request.headers['X-API-KEY'])
        try:
            evaluator = getEvalFromMail(mail)
            if evaluator is None: return UNKNOWN_USER_RESPONSE
            group = getGroupFromId(group_id)
            if group is None: return GROUP_DOES_NOT_EXIST
            if group[GROUPS_ID_EVAL_FIELD] != evaluator['_id']: return GROUP_DOES_NOT_EXIST
            formatedGroup = formatGroupForEval(group, evaluator['_id'])
            return {'status': 0, 'group': formatedGroup}
        except PyMongoError:
            return DATABASE_QUERY_ERROR


@api.route('/get/candidate/group_assignment/<string:group_id>/<string:assign_id>')
class GetGroupAssignment(Resource):

    @api.doc(security='apikey', responses={
        200: 'Query went OK, response in the \'assignment\' tag.',
        403: 'Wrong user type, this route require a candidate',
        404: 'Either user, group, assignment does not exist or the user is not part of this group or assignment not '
             'assigned to the group.',
        503: 'Error with the database'
    })
    @token_requiered
    def get(self, group_id, assign_id):
        """
            Not sure about the use of that route, not implemented yet - DONT USE.
        """
        mail = decodeAuthToken(request.headers['X-API-KEY'])
        try:
            candidate = getCandidateFromMail(mail)
            if candidate is None: return UNKNOWN_USER_RESPONSE
            group = getGroupFromId(groupID=group_id)
            if group is None: return GROUP_DOES_NOT_EXIST
            if candidate['_id'] not in [cand_id for cand_id in
                                        group[GROUPS_CANDIDATES_IDS_FIELD]]: return CANDIDATE_NOT_IN_GROUP
            assignment = getAssignmentFromId(assign_id)
            if assignment is None: return ASSIGNMENT_DOES_NOT_EXIST
            if assignment['_id'] not in [a[GROUPS_ASSIGNMENTS_IDS_FIELD]
                                         for a in group[GROUPS_ASSIGNMENTS_FIELD]]: return ASSIGNMENT_NOT_ASSIGNED_TO_GROUP
            return {'status': 0, 'assignment': formatAssignForCandidate(groupAssign=group[GROUPS_ASSIGNMENTS_FIELD]['e'], candidateID=candidate['_id'])}
        except ConnectDatabaseError:
            return DATABASE_QUERY_ERROR
        except WrongUserTypeException:
            return WRONG_USER_TYPE

updateNameModel = api.model('Update name model', {
    'group_id': fields.String('Id of the group to update'),
    'new_name': fields.String('New name of the group')
})

@api.route('/update/name')
class RenameGroup(Resource):

    PUT_FIELDS = [field for field in updateNameModel]

    @token_requiered
    @api.expect(updateNameModel)
    @api.doc(security='apikey', responses={
        200: 'query went OK',
        403: str(GROUP_NAME_ALREADY_EXISTS[0]),
        404: str(UNKNOWN_USER_RESPONSE[0]),
        422: str(UNPROCESSABLE_ENTITY_RESPONSE[0]),
        503: str(DATABASE_QUERY_ERROR[0])
    })
    def put(self):
        if not all(x in api.payload for x in self.PUT_FIELDS) or \
                len(self.PUT_FIELDS) != len(api.payload): return UNPROCESSABLE_ENTITY_RESPONSE
        mail = decodeAuthToken(request.headers['X-API-KEY'])
        try:
            evaluator = getEvalFromMail(mail)
            if evaluator is None: return UNKNOWN_USER_RESPONSE
            groups = getAllEvalGroups(evaluator['_id'])
            if api.payload['group_id'] in [g[GROUPS_NAME_FIELD] for g in groups]: return GROUP_NAME_ALREADY_EXISTS
            updateGroupName(api.payload['group_id'], api.payload['new_name'])
            return BASIC_SUCCESS_RESPONSE
        except ConnectDatabaseError:
            return DATABASE_QUERY_ERROR

@api.route('/evaluator/remove/candidate')
class RemoveCandidateOfGroup(Resource):

    @token_requiered
    @api.doc(security='apikey', responses={
        503: str(DATABASE_QUERY_ERROR[0])
    })
    def put(self):
        mail = decodeAuthToken(request.headers['X-API-KEY'])
        try:
            pass
        except ConnectDatabaseError:
            return DATABASE_QUERY_ERROR