from flask_restplus import Namespace, Resource, fields
from core.Utils.Constants import *
from core.Utils.DatabaseHandler import DatabaseHandler
from core.Utils.Utils import hashStr

api = Namespace('users', description="Users related operations.")

userEval = api.model('UserEvaluator', {'name': fields.String('Name of the user.'),
                            'lastname': fields.String('Lastname of the user.'),
                            'email': fields.String('Mail of the user.'),
                            'password': fields.String('Password of the user.'),
                            "organisation": fields.String('Organisation of the user.')
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

db = DatabaseHandler(DB_IP, DB_PORT)
db.connect()

@api.route('/')
class Users(Resource):

    def get(self):
        items = db.getCollectionItems(USERS_DOCUMENT)
        for i in items:
            i["_id"] = str(i['_id'])
        return {"users": items}

@api.route('/Login')
class UserLogin(Resource):

    @api.expect(userModel)
    def post(self):
        print("coucou")
        print(api.payload)
        return {"id": "coucou"}



@api.route('/Eval')
class HandlingUsers(Resource):

    def get(self):
        items = db.getCollectionItems(EVALUATORS_DOCUMENT)
        for i in items:
            i["_id"] = str(i['_id'])
            i["user_id"] = str(i['user_id'])
        return {"users": items}

    @api.expect(userEval)
    def post(self):
        """
            Create a Evaluator User.
        :return:
        """
        try:
            if api.payload["email"] in db.getAllUsersMail(): return {'status': -1, "error": "Adresse email déjà"
                                                                                            "présente dans la base"
                                                                                            "de données."}
            user = USERS_ITEM_TEMPLATE
            user["name"] = api.payload["name"]
            user["lastname"] = api.payload["lastname"]

            # Encrypt password

            user["password"] = hashStr(api.payload["password"])
            user["email"] = api.payload["email"]

            idUser = db.insert(USERS_DOCUMENT, user.copy())

            eval = EVALUATORS_ITEM_TEMPLATE
            eval["user_id"] = idUser.inserted_id
            eval["organisation"] = api.payload["organisation"]
            db.insert(EVALUATORS_DOCUMENT, dict(eval).copy())

            return {"status": 0}
        except Exception as e:
            return {"status": "-1", "error" : "Il y a eu une erreur lors de la création de l'utilisateur" +str(e.args)}


@api.route('/Eval/<string:userId>/AddOneCand/<string:mail>')
class EvalAddCand(Resource):

    def post(self, userId, mail):
        if mail in db.getAllUsersMail():
            return {"info": "Le mail est présent dans la base de données, cette fonctionnalité n'est pas encore présente dans l'API, elle le sera bientôt"}
        else:
            return {"info": "Le mail n'est pas présent dans la base de données, cette fonctionnalité n'est pas encore implémentée dans l'API."}

@api.route('/Eval/<string:userId>/AddManyCand')
class EvalAddManyCand(Resource):

    @api.expect(addManyCandModel)
    def post(self, userId):
        return {"maillist": api.payload["mailList"]}