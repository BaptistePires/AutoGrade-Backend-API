#####################
##  DB Constants   ##
#####################
# Connections
DB_IP = "127.0.0.1"
DB_PORT = 27017

# Fields
USERS_DOCUMENT = "users"
USERS_ITEM_TEMPLATE = {
    "name": "",
    "lastname": "",
    "password": "",
    "mail": "",
    "groups": [],
    "assigments": []
}

EVALUATORS_DOCUMENT = "evaluators"
EVALUATORS_ITEM_TEMPLATE = {
    "user_id": "",
    "organisation": ""
}

#########
# PATHS #
#########
ASSIGMENTS_DIR = 'AISSIGNMENT_FILES'
