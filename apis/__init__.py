from flask_restplus import Api
from .Users import api as usersNs
from .Groups import api as groupsNs
from .Assignments import api as assignNs
from functools import wraps


authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-KEY'
    }
}
api = Api(authorizations=authorizations, security='apiKey', version='0.1', title='AutoGrade-API', description='', validate=True)
api.add_namespace(usersNs, path='/Users')
api.add_namespace(groupsNs, path='/Groups')
api.add_namespace(assignNs, path='/Assignments')

