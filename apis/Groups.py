from flask_restplus import Namespace, Resource, fields
from core.Utils.Constants import *
from core.Utils.DatabaseHandler import DatabaseHandler
from bson.objectid import ObjectId

api = Namespace('groups', description="Groups related operations.")


groupModel = api.model('group', {
    'name': fields.String('Group\' name.'),
    'assignments': fields.List(fields.String)
})

db = DatabaseHandler(DB_IP, DB_PORT)
db.connect()

@api.route('/')
class Groups(Resource):

    def get(self):
        items = db.getCollectionItems('groups')
        for i in items:
            i["assignments"] = [str(idAss) for idAss in i["assignments"]]
            i["_id"] = str(i["_id"])

        return {'groups' :items}

    @api.expect(groupModel)
    def post(self):
        print(api.payload)
        db.insert('groups', api.payload)

@api.route('/<string:field>')
class GroupIdGet(Resource):

    def get(self, field):
        try:
            items = db.getCollectionItems('groups')

            return [str(grp[field]) for grp in items]
        except Exception as e:
            # TODO : Throw & handle exception when field is not found
            pass

@api.route('/GetOne/<string:id>')
class SingleGroupAction(Resource):

    def get(self, id):
        try:
            items = db.findOneItemByColAndId('groups', ObjectId(id))
            print(items)
            return items

        except Exception as e:
            # TODO : HANDLE EX
            print(e)
            pass