UNKNOW_USER_RESPONSE = {'status': -1, 'error': 'Utilisateur inextistant'}
BASIC_SUCCESS_RESPONSE = {'status': 0}
UNPROCESSABLE_ENTITY_RESPONSE = {'stauts': -1, 'error': 'Body of the request does not match the expected one. Check documentaton for more informaton.'}
WRONG_USER_TYPE = {'status': -1, 'error': 'The user type (evaluator/candidate) is the one required for this.'}
MAIL_NOT_MATCHING_TOKEN = {'status': -1, 'error': 'Token and mail provided do not match.'}
TOKEN_EXPIRED = {'status': -1, 'error': 'Token has expired, please login again.'}
GROUP_DOES_NOT_EXIST = {'status': -1, 'error': 'The group does not exist.'}
USER_ALREADY_IN_GROUP = {'status': -1, 'error': 'The user is already in the group.'}