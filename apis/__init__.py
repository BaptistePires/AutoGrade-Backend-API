from flask_restplus import Api
from .Users import api as usersNs
from .Groups import api as groupsNs

api = Api(version='0.1', title='AutoGrade-API', description='', validate=True)
api.add_namespace(usersNs, path='/Users')
api.add_namespace(groupsNs, path='/Groups')








