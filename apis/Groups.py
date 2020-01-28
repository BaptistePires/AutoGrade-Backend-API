from flask_restplus import Namespace, Resource, fields
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
    'mail_eval': fields.String('Evaluator mail address'),
    'name': fields.String('Group\' name.')
})

addUserModel = api.model('addUserToGroupModel', {
    'mail_eval': fields.String('Evaluator mail address'),
    'name': fields.String('Group\' name.'),
    'user_mail': fields.String('Mail address of the user')
})


@api.route('/ClearDb')
class ClearDb(Resource):

    def get(self):
        db.clearDocument(GROUPS_DOCUMENT)


@api.route('/Create')
class CreateGroup(Resource):

    @api.expect(groupModel)
    @token_requiered
    @api.doc(security='apikey')
    def post(self):
        try:
            if not validateToken(api.payload['mail_eval'], request.headers['X-API-KEY']):
                return {'stauts': -1, 'error': 'Token invalide'}
            eval = getEvalFromMail(api.payload["mail_eval"].lower())
            if eval is None: return UNKNOW_USER_RESPONSE
            if api.payload['name'] in getAllGroupNameFromEvalId(eval['_id']): return GROUP_NAME_ALREADY_EXISTS
            group = GROUP_TEMPLATE
            group['id_eval'] = eval['_id']
            group['name'] = api.payload['name']
            result = db.insert(GROUPS_DOCUMENT, group.copy())
            db.addGroupToUser(eval['_id'], result.inserted_id)
            addGroupToEval(eval['_id'], result.inserted_id)
            createFolderForGroup(result.inserted_id)
            return BASIC_SUCCESS_RESPONSE
        except errors.ServerSelectionTimeoutError as e:
            return {'status': -1, 'error': 'Impossible de se connecter au serveur de la base de données.'}
        except ExpiredTokenException:
            return TOKEN_EXPIRED, 401
        except InvalidTokenException:
            return MAIL_NOT_MATCHING_TOKEN, 401
        except ConnectDatabaseError:
            return DATABASE_QUERY_ERROR


@api.route('/GetOneBy/Mail/Name')
class GetOneMailName(Resource):

    @api.expect(groupModel)
    def post(self):
        try:
            eval = db.getOneUserByMail(api.payload['mail_eval'])
            if eval is None: return {'status': -1, 'error': 'Utilisateur inextistant.'}
            group = db.getGroupByEvalIdAndName(eval['_id'], api.payload['name'].lower())
            if group is None: return {'status': -1, 'error': 'Groupe inexistant.'}
            candMails = [db.getUserMailById(i) for i in group['candidates_ids']]
            group.pop('_id')
            group.pop('id_eval')
            group.pop('candidates_ids')
            group['candidates_mail'] = candMails
            return {'status': 0, 'group': group}
        except ConnectDatabaseError:
            return DATABASE_QUERY_ERROR


@api.route('/AddUser/MailEval/Name')
class addUserToGroup(Resource):

    @api.expect(addUserModel)
    def post(self):
        try:
            eval = db.getOneUserByMail(api.payload['mail_eval'])
            if eval is None: return UNKNOW_USER_RESPONSE
            group = db.getGroupByEvalIdAndName(eval['_id'], api.payload['name'].lower())
            user = db.getOneUserByMail(api.payload['user_mail'].lower())
            if user is None: return UNKNOW_USER_RESPONSE
            uAdd = db.addGroupToUser(user['_id'], group['_id'])
            gAdd = db.addUserToGroup(group['_id'], user['_id'])
            if uAdd is not None and gAdd is not None:
                return {"status": 0}
            else:
                return {'stauts': -1, 'error': 'Il y a eu une erreur lors de l\'ajout au groupe.'}
        except ConnectDatabaseError:
            return DATABASE_QUERY_ERROR


@api.route('/Get/AllByMail/<mail>')
class getAllByMail(Resource):

    def post(self, mail):
        try:
            mail = mail.lower()
            user = db.getOneUserByMail(mail)
            if user is None: return UNKNOW_USER_RESPONSE
            groups = db.getAllGroupsFromMail(mail)
            return BASIC_SUCCESS_RESPONSE
        except ConnectDatabaseError:
            return DATABASE_QUERY_ERROR


@api.route('/evaluator/get/all/<string:mail>')
class evalGetAllGroup(Resource):

    @token_requiered
    @api.doc(security='apikey', responses= {401: 'Mail not matching token.',
                                            404: 'User unknow or wrong type (evaluator required',
                                            503: 'Error with the database, please try again later.'})
    def get(self, mail):
        try:
            if not validateToken(mail, request.headers['X-API-KEY']): return MAIL_NOT_MATCHING_TOKEN
            eval = getEvalFromMail(mail)
            if eval is None: return UNKNOW_USER_RESPONSE
            groups = [getGroupFromId(g) for g in eval[EVALUATOR_GROUPS_FIELD]]
            return {'status': 0, 'groups': dumps(groups)}, 200
        except ConnectDatabaseError:
            return DATABASE_QUERY_ERROR



addAssignmentToGoupModel = api.model('Add assignment to group model', {
    'mail_eval': fields.String('Mail of the evaluator of the group (must be the current user)'),
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
        if not validateToken(api.payload['mail_eval'], request.headers['X-API-KEY']): return MAIL_NOT_MATCHING_TOKEN
        try:
            eval = getEvalFromMail(api.payload['mail_eval'])
            if eval is None: return UNKNOW_USER_RESPONSE
            groups = getAllGroupsFromUserId(eval['_id'])
            if api.payload['group_name'] not in [g[GROUPS_NAME_FIELD] for g in groups]: return GROUP_DOES_NOT_EXIST
            group = None
            print(groups)
            for g in groups:
                if g[GROUPS_NAME_FIELD] == api.payload['group_name']:
                    group = g
            assign = getAssignmentFromId(api.payload['assignID'])
            if assign is None: return ASSIGNMENT_DOES_NOT_EXIST
            print('a', group[GROUPS_ASSIGNMENTS_FIELD])
            if assign['_id'] in [x[GROUPS_ASSIGNMENTS_IDS_FIELD] for x in group[GROUPS_ASSIGNMENTS_FIELD]]: return ASSIGNMENT_ALREADY_ASSIGNED_TO_GROUP
            deadline = datetime.strptime(api.payload['deadline'], '%Y/%m/%d %H:%M:%S')
            if isDateBeforeNow(deadline): return DATE_BEFORE_NOW
            addAssignToGroup(groupId=group['_id'], assignId=assign['_id'], deadline=deadline)
            createFolderAssignmentForGroup(group['_id'], assign['_id'])
            return BASIC_SUCCESS_RESPONSE
        except ConnectDatabaseError:
            return DATABASE_QUERY_ERROR
        except GroupDoesNotExistException:
            return GROUP_DOES_NOT_EXIST
