from flask_restplus import Namespace, Resource, fields
from core.Utils.Constants.DatabaseConstants import EVALUATORS_DOCUMENT, USERS_DOCUMENT
from core.Utils.Constants.ApiModels import EVALUATORS_ITEM_TEMPLATE, USERS_ITEM_TEMPLATE
from core.Utils.Constants.ErrorsStringConstants import *
from core.Utils.Constants.UtilsStringConstants import CONTENT_MAIL_CONF
from core.Utils.DatabaseHandler import DatabaseHandler
from core.Utils.Utils import *

from core.Utils.MailHandler import MailHandler
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
                            "organisation": fields.String('Organisation of the user.'),
                            'confirmed': fields.Boolean('Is the account confirmed')
                              })

userCand = api.model('UserCandidate', {'name': fields.String('Name of the user.'),
                                'lastname': fields.String('Lastname of the user.'),
                                'email': fields.String('Mail of the user.'),
                                "organisation": fields.String('Organisation of the user.')
                              })

userModel = api.model('UserModel', {
    'email': fields.String(),
    'password': fields.String()
})

addManyCandModel = api.model('addManyCand', {
    'mailList': fields.List(fields.String)
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

@api.route('/Login')
class UserLogin(Resource):

    @api.expect(userModel)
    def post(self):
        userInDb = db.getOneUserByMail(api.payload["email"])
        if userInDb is None: return {'status': -1, 'error': 'Email ou mot de passe incorrect'}
        else:
            if not checkPw(api.payload["password"], userInDb['password']):return {'status': -1, 'error': MAIL_OR_PASS_ERR}
            else:
                token = encodeAuthToken(str(userInDb['_id']))
                #print(decodeAuthToken(token))
                #print(userInDb['_id'])
                return {"status": 0, "auth_token": token}

@api.route('/Confirmation/<string:token>')
class userConfirmation(Resource):

    def get(self, token):
        try:
            mail = validateConfToken(token)
            user = db.getOneUserByMail(mail)
            if user != None:
                if user["confirmed"]:
                    #TODO : return good response
                    return {'status': -1, 'error': 'Wrong token1'}
                else:
                    db.updateConfirmationOfUserWithMail(mail)
            else:
                return {'status': -1, 'error': 'Wrong token2'}
            return {'status': 0}
        except Exception as e:
            return {'status': -1, 'error': 'Wrong token3'}
###########################
# Evaluators users routes #
###########################

@api.route('/Eval')
class HandlingUsers(Resource):

    @api.hide
    def get(self):
        items = db.getCollectionItems(EVALUATORS_DOCUMENT)
        for i in items:
            i["_id"] = str(i['_id'])
            i["user_id"] = str(i['user_id'])
        return {"users": items}

    @api.expect(userEval)
    def post(self):
        """
            Create a Evaluator User. Send mail de confirmation # TODO send mail
        :return:
        """
        try:
            if api.payload["email"] in db.getAllUsersMail(): return {'status': -1, "error": MAIL_ALREADY_USED_ERR}

            if not checkEmailFormat(api.payload['email']): return {'status': -1, 'error': WRONG_MAIL_FORMAT_ERR}
            user = setupUserDictFromHTTPPayload(api.payload)
            idUser = db.insert(USERS_DOCUMENT, user.copy())
            eval = EVALUATORS_ITEM_TEMPLATE
            eval["user_id"] = idUser.inserted_id
            eval["organisation"] = api.payload["organisation"]
            db.insert(EVALUATORS_DOCUMENT, dict(eval).copy())
            createFolderForUserId(eval["user_id"])
            MailHandler.sendPlainTextMail(user["email"], "Inscription à AutoGrade !", CONTENT_MAIL_CONF.format(token=generateMailConfToken(user["email"])))
            return {"status": 0}
        except Exception as e:
            print(e)
            return {"status": -1, "error" : WRONG_MAIL_FORMAT_ERR + " " + str(e.args)}


@api.route('/Eval/<string:userId>/AddOneCand/<string:mail>')
class EvalAddCand(Resource):

    def post(self, userId, mail):
        # TODO : Insert an user in the database but : If he's not already registered then we need to send a mail (
        # TODO : will implements that later) to the user to allow him to create an account.
        # TODO : Otherwise, we need to add the user linked to the mail to the group the (need to add that to the route)
        if mail in db.getAllUsersMail():
            return {"info": "Le mail est présent dans la base de données, cette fonctionnalité n'est pas encore présente dans l'API, elle le sera bientôt"}
        else:
            return {"info": "Le mail n'est pas présent dans la base de données, cette fonctionnalité n'est pas encore implémentée dans l'API."}

@api.route('/Eval/<string:userId>/AddManyCand')
class EvalAddManyCand(Resource):

    @api.expect(addManyCandModel)
    def post(self, userId):
        # TODO : Call @api.route('/Eval/<string:userId>/AddOneCand/<string:mail>') to add all mails.
        return {"maillist": api.payload["mailList"]}

###########################
# Candidates users routes #
###########################
