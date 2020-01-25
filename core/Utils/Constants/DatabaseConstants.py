#########################
# Database network conf #
#########################
DB_IP = "127.0.0.1"
DB_PORT = 27017

###################
# Documents names #
###################
USERS_DOCUMENT = "users"
EVALUATORS_DOCUMENT = "evaluators"
CANDIDATES_DOCUMENT = "candidates"
GROUPS_DOCUMENT = "groups"

####################
#   Fields names   #
####################
# USERS / EVALUATORS / CANDIDATES #
# Generals
MAIL_FIELD = "email"
NAME_FIELD = "name"
LASTNAME_FIELD = "lastname"
PASSWORD_FIELD = "password"
CONFIRMED_FIELD = "confirmed"
TYPE_FIELD = "type"
EVALUATOR_TYPE = 'evaluator'
CANDIDATE_TYPE = 'candidate'

# Evaluators & candidates #
USER_ID_FIELD = 'user_id'
ORGANISATION_FIELD = 'organisation'

# Candidates #
CANDIDATES_GROUPS_FIELD = 'groups'

# Evaluator #
EVALUATOR_GROUPS_FIELD ='groupsInCharge'
EVALUATOR_ASSIGNMENTS_FIELD = 'assignmentsCreated'

# GROUPS #
GROUPS_ID_EVAL_FIELD = 'id_eval'
GROUPS_NAME_FIELD = 'name'
GROUPS_ASSIGNMENTS_IDS_FIELD = 'assignments_ids'
GROUPS_CANDIDATES_IDS_FIELD = 'candidates_ids'

# Assignments #
ASSIGNMENT_NAME = 'name'
ASSIGNMENT_FILENAME = 'filename'
ASSIGNMENT_AUTHOR_ID = 'author_id'
ASSIGNMENT_DESCRIPTION = 'description'
ASSIGNMENT_DEADLINE = 'deadline'


# Templates to fill
EVALUATORS_ITEM_TEMPLATE = {
    USER_ID_FIELD: "",
    ORGANISATION_FIELD: "",
    EVALUATOR_GROUPS_FIELD: [],
    EVALUATOR_ASSIGNMENTS_FIELD: []
}

CANDIDATES_ITEM_TEMPLATE = {
    USER_ID_FIELD: '',
    ORGANISATION_FIELD: '',
    CANDIDATES_GROUPS_FIELD: []
}

USERS_ITEM_TEMPLATE = {
    NAME_FIELD: "",
    LASTNAME_FIELD: "",
    PASSWORD_FIELD: "",
    MAIL_FIELD: "",
    CONFIRMED_FIELD: False,
    TYPE_FIELD: ""
}

ASSIGNMENT_ITEM_TEMPLATE = {
    ASSIGNMENT_NAME: '',
    ASSIGNMENT_FILENAME: '',
    ASSIGNMENT_AUTHOR_ID: '',
    ASSIGNMENT_DESCRIPTION: '',
    ASSIGNMENT_DEADLINE: None,

}