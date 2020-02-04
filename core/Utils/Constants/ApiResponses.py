from core.Utils.Constants.DatabaseConstants import *
from json import dumps
from flask_restplus import api, fields

###################
#   STATUS CODE   #
###################
SUCCESS_CODE = 0
BASIC_ERROR_CODE = -1
UNKNOWN_USER_ERROR_CODE = -2
DATABASE_QUERY_ERROR_CODE = -3
BODY_CONTENT_ERROR_CODE = -4
TOKENS_ERROR_CODE = -5

###################
# HTTPS RESPONSES #
###################

UNKNOWN_USER_RESPONSE = {'status': UNKNOWN_USER_ERROR_CODE, 'error': 'Utilisateur inextistant'}, 404
CANDIDATE_ADDED_RESPONSE = {'status': 0, 'infos': 'Group added to the user.'}, 200
PASSWORD_NOT_STRONG_ENOUGH = {'status': BODY_CONTENT_ERROR_CODE, 'error': 'The password is not strong enough, it musts'
                                                                          ' contains 1 lower case and 1 upper case'
                                                                          ' letter, 1 special character, 1 number'
                                                                          'and have a length between 6 and 20 '
                                                                          'characters.'}, 400
BASIC_SUCCESS_RESPONSE = {'status': SUCCESS_CODE}, 200
BASIC_ERROR_RESPONSE = {'status': BASIC_ERROR_CODE, 'error': 'An error occurred, please try again.'}, 400
UNPROCESSABLE_ENTITY_RESPONSE = {'stauts': BODY_CONTENT_ERROR_CODE,
                                 'error': 'Body of the request does not match the expected one. Check documentaton for more informaton.'}, 422
WRONG_USER_TYPE = {'status': BASIC_ERROR_CODE, 'error': 'The user type is not the one required for this request.'}, 403
MAIL_NOT_MATCHING_TOKEN = {'status': TOKENS_ERROR_CODE, 'error': 'Token and mail provided do not match.'}, 401
INVALID_TOKEN = {'status': TOKENS_ERROR_CODE, 'error': 'Token provided is invalid.'}, 401
TOKEN_EXPIRED = {'status': TOKENS_ERROR_CODE, 'error': 'Token has expired, please login again.'}, 401
GROUP_DOES_NOT_EXIST = {'status': BASIC_ERROR_CODE, 'error': 'The group does not exist.'}, 404
USER_ALREADY_IN_GROUP = {'status': BASIC_ERROR_CODE, 'error': 'The user is already in the group.'}, 409
CONF_TOKEN_SIGN_EXPIRED = {'status': TOKENS_ERROR_CODE, 'error': 'The confirmation token has expired'}, 401
CONF_TOKEN_BAD_SIGNATURE = {'status': TOKENS_ERROR_CODE, 'error': 'The token has a wrong signature'}, 401
DATABASE_QUERY_ERROR = {'status': DATABASE_QUERY_ERROR_CODE, 'error': 'Error while connecting to the databse.'}, 503
MAIL_ADDR_ALREADY_CONFIRMED = {'status': BASIC_ERROR_CODE, 'error': 'Mail address already confirmed'}, 409
WRONG_PASS_OR_MAIL = {'status': BASIC_ERROR_CODE, 'error': 'Wrong mail or password'}, 404
MAIL_NOT_CONFIRMED = {'status': BASIC_ERROR_CODE, 'error': 'Account not confirmed'}, 401
MAIL_NOT_AVAILABLE = {'status': BASIC_ERROR_CODE, 'error': 'This mail address is already in use.'}, 409
WRONG_MAIL_FORMAT = {'status': BODY_CONTENT_ERROR_CODE, 'error': 'There is an error with the mail you submitted.'}, 400
ASSIGNMENT_FILE_REQUESTED = {'status': BODY_CONTENT_ERROR_CODE, 'error': 'Assignment file missing'}, 400
FILE_TYPE_NOT_ALLOWED = {'stauts': BODY_CONTENT_ERROR_CODE, 'error': 'This file extension is not allowed !'}, 400
ASSIGNMENT_ADDED_SUCCESS = {'status': BASIC_ERROR_CODE,
                            'info': 'Assignment was added successfully, we are currently checking it, it\'s status '
                                    'will be updated soon...'}, 200
GROUP_NAME_ALREADY_EXISTS = {'status': BASIC_ERROR_CODE,
                             'error': 'Group name already exists. Please chose another one.'}, 403
DATE_BEFORE_NOW = {'status': BASIC_ERROR_CODE, 'error': 'You can\'t use a date that is before now.'}, 403
ASSIGNMENT_DOES_NOT_EXIST = {'status': BASIC_ERROR_CODE, 'error': 'The assignment you requested does not exist.'}, 404
ASSIGNMENT_NOT_ASSIGNED_TO_GROUP = {'status': BASIC_ERROR_CODE,
                                    'error': 'This group does not have this assignment.'}, 404
ASSIGNMENT_ALREADY_ASSIGNED_TO_GROUP = {'status': BASIC_ERROR_CODE,
                                        'error': 'The assignment you tried to add to the group is already assigned to '
                                                 'this one.'}, 403
CANDIDATE_NOT_IN_GROUP = {'status': BASIC_ERROR_CODE, 'error': 'The candidate is not part of that group.'}, 404
WRONG_MARKING_SCHEME = {'status': BODY_CONTENT_ERROR_CODE,
                        'error': 'There is an error with the marking scheme you submitted, etiher there are missing '
                                 'fields of the sum of all fields is not 100.'}, 400
TRANSACTION_ALREADY_REGISTERED= {'status': -1, 'error': 'The transaction you requested already has been registred, if'
                                                        'you have any issue, please contact us.'}, 409
PAYPAL_API_CONNECT_ERROR = {'status': -1, 'error': 'Can\'t connect to the PayPal API.'}
AMOUNT_NOT_ALLOWED = {'status':-1, 'error': 'The amount you requested is not supported by this app.'}, 400
EVALUATOR_NOT_PREMIUM = {'status': -1, 'error': 'You need to be premium to create another group'}, 400

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
    ASSIGNMENT_INPUT_OUTPUTS: fields.List(
        fields.String('List of inpus/outputs to provide to the program. formated like that : "inputs : output')),
    # ASSIGNMENT_STATISTICS_NAME: fields.Nested(ASSIGNMENT_STATISTICS_RESPONSE_TEMPLATE)
}
