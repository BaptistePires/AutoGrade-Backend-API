from flask_restplus import Namespace, Resource, fields
from core.Utils.Constants.DatabaseConstants import DB_IP, DB_PORT, GROUPS_DOCUMENT
from core.Utils.DatabaseHandler import DatabaseHandler
from bson.objectid import ObjectId
from core.Utils.Constants.ApiResponses import *
from pymongo import errors
from flask import session
from flask_jwt_extended import jwt_required
from core.Utils.Utils import token_requiered, validateToken
from flask import request

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

GROUP_TEMPLATE = {
    'id_eval': '',
    'name': '',
    'assginemnts_ids': [],
    'candidates_ids': []
}
db = DatabaseHandler()
db.connect()

@api.route('/ClearDb')
class ClearDb(Resource):

    def get(self):
        db.clearDocument(GROUPS_DOCUMENT)

@api.route('/Create')
class CreateGroup(Resource):

    @api.expect(groupModel)
    @token_requiered
    @api.doc(security='apiKey')
    def post(self):
        try:
            if not validateToken(api.payload['mail_eval'], request.headers['X-API-KEY']):
                return {'stauts': -1, 'error': 'Token invalide'}
            eval = db.getOneUserByMail(api.payload["mail_eval"].lower())
            if eval is None: return UNKNOW_USER_RESPONSE
            group = GROUP_TEMPLATE
            group['id_eval'] = str(eval['_id'])
            group['name'] = api.payload['name']
            result = db.insert(GROUPS_DOCUMENT, group.copy())
            db.addGroupToUser(eval['_id'], result.inserted_id)
        except errors.ServerSelectionTimeoutError as e :
            return {'status': -1, 'error': 'Impossible de se connecter au serveur de la base de données.'}
        return BASIC_SUCCESS_RESPONSE
        return "{}"

@api.route('/GetOneBy/Mail/Name')
class GetOneMailName(Resource):

    @api.expect(groupModel)
    def post(self):
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

@api.route('/AddUser/MailEval/Name')
class addUserToGroup(Resource):

    @api.expect(addUserModel)
    def post(self):
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
            print(uAdd, " ", gAdd)
            return {'stauts': -1, 'error': 'Il y a eu une erreur lors de l\'ajout au groupe.'}

@api.route('/Get/AllByMail/<mail>')
class getAllByMail(Resource):

    def post(self, mail):
        mail = mail.lower()
        user = db.getOneUserByMail(mail)
        if user is None: return UNKNOW_USER_RESPONSE
        groups = db.getAllGroupsFromMail(mail)
        print(groups)

        return BASIC_SUCCESS_RESPONSE
