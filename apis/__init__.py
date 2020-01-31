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
api = Api(authorizations=authorizations, version='1.3', title='AutoGrade-API', description='This this all the routes '
                                                                                           'for the backend of the '
                                                                                           'project AutoGrade', validate=True)
api.add_namespace(usersNs, path='/users')
api.add_namespace(groupsNs, path='/groups')
api.add_namespace(assignNs, path='/assignments')

