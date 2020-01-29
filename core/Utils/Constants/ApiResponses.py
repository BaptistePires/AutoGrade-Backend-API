from core.Utils.Constants.DatabaseConstants import *
from json import dumps
from flask_restplus import api, fields
###################
# HTTPS RESPONSES #
###################

UNKNOW_USER_RESPONSE = {'status': -1, 'error': 'Utilisateur inextistant'}, 404
BASIC_SUCCESS_RESPONSE = {'status': 0}, 200
BASIC_ERROR_RESPONSE = {'status': -1, 'error': 'An error occurred, please try again.'}, 400
UNPROCESSABLE_ENTITY_RESPONSE = {'stauts': -1,
                                 'error': 'Body of the request does not match the expected one. Check documentaton for more informaton.'}, 422
WRONG_USER_TYPE = {'status': -1, 'error': 'The user type is not the one required for this request.'}, 403
MAIL_NOT_MATCHING_TOKEN = {'status': -1, 'error': 'Token and mail provided do not match.'}, 401
INVALID_TOKEN = {'status': -1, 'error': 'Token provided is invalid.'}, 401
TOKEN_EXPIRED = {'status': -1, 'error': 'Token has expired, please login again.'}, 401
GROUP_DOES_NOT_EXIST = {'status': -1, 'error': 'The group does not exist.'}, 404
USER_ALREADY_IN_GROUP = {'status': -1, 'error': 'The user is already in the group.'}, 409
CONF_TOKEN_SIGN_EXPIRED = {'status': -1, 'error': 'The confirmation token has expired'}, 401
CONF_TOKEN_BAD_SIGNATURE = {'status': -1, 'error': 'The token has a wrong signature'}, 401
DATABASE_QUERY_ERROR = {'status': -1, 'error': 'Error while connecting to the databse.'}, 503
MAIL_ADDR_ALREADY_CONFIRMED = {'status': -1, 'error': 'Mail address already confirmed'}, 409
WRONG_PASS_OR_MAIL = {'status': -1, 'error': 'Wrong mail or password'}, 404
MAIL_NOT_CONFIRMED = {'status': -1, 'error': 'Account not confirmed'}, 401
MAIL_NOT_AVAILABLE = {'status': -1, 'error': 'This mail address is already in use.'}, 409
WRONG_MAIL_FORMAT = {'status': -1, 'error': 'There is an error with the mail you submitted.'}, 400
ASSIGNMENT_FILE_REQUESTED = {'status': -1, 'error': 'Assignment file missing'}, 400
FILE_TYPE_NOT_ALLOWED = {'stauts': -1, 'error': 'This file extension is not allowed !'}, 400
ASSIGNMENT_ADDED_SUCCESS = {'status': 0,
                            'info': 'Assignment was added successfully, we are currently checking it, it\'s status will be updated soon...'}
GROUP_NAME_ALREADY_EXISTS = {'status': -1, 'error': 'Group name already exists. Please chose another one.'}, 403
DATE_BEFORE_NOW = {'status': -1, 'error': 'You can\'t use a date that is before now.'}, 403
ASSIGNMENT_DOES_NOT_EXIST = {'status': -1, 'error': 'The assignment you requested does not exist.'}, 404
ASSIGNMENT_NOT_ASSIGNED_TO_GROUP = {'status': -1, 'error': 'This group does not have this assignment.'}
ASSIGNMENT_ALREADY_ASSIGNED_TO_GROUP = {'status': -1,
                                        'error': 'The assignment you tried to add to the group is already assigned to this one.'}, 403
CANDIDATE_NOT_IN_GROUP = {'status': -1, 'error': 'The candidate is not part of that group.'}, 404

###################
# MODELS RETURNED #
###################

from flask_restplus import Model
ASSIGNMENT_STATISTICS_RESPONSE_TEMPLATE = {
    ASSIGNMENT_STAT_TIME: fields.Float('Represents the amount of time took by the program to complete'),
    ASSIGNMENT_FILE_SIZE: fields.Integer('Represents the size of the program in bytes.')
}
EVALUATOR_ASSIGNMENT_RESPONSE_TEMPLATE = {
    'id': fields.String('Id of the assignment'),
    ASSIGNMENT_NAME: fields.String('Name of the assignement'),
    ASSIGNMENT_DESCRIPTION: fields.String('Description of the assignment'),
    ASSIGNMENT_IS_VALID: fields.Integer('Possibles values : -1; 0; 1. -1 : Means that the assignment is not valid'
                                        ' (Issue with I/Os), the program itself, etc... 0 : Means that the program'
                                        'is being checked by the system, should update soon and 1 means that everything is fine with the program.'),
    ASSIGNMENT_INPUT_OUTPUTS: fields.List(fields.String('List of inpus/outputs to provide to the program. formated like that : "inputs : output')),
    # ASSIGNMENT_STATISTICS_NAME: fields.Nested(ASSIGNMENT_STATISTICS_RESPONSE_TEMPLATE)
}