from werkzeug import datastructures
from flask_restplus import Namespace, Resource, fields, marshal_with
from flask import request
from flask_restplus import reqparse
from core.Utils.Constants.ApiResponses import *
import core.Utils.Constants.Constants as generalConsts
from core.Utils.DatabaseFunctions.AssignmentsFunctions import addAssignment, getAllAssignmentsForEval
from core.Utils.Exceptions.ConnectDatabaseError import ConnectDatabaseError
from core.Utils.Utils import *
from core.Utils.DatabaseFunctions.UsersFunctions import *
from core.Utils.DatabaseFunctions.AssignmentsFunctions import *
from core.Utils.DatabaseFunctions.GroupsFunctions import *
from datetime import datetime

import json

api = Namespace('Assignments', description="Assignments related operations.")
##############
# API models #
##############
# evalGetTemplate = EVALUATOR_ASSIGNMENT_RESPONSE_TEMPLATE
# evalGetTemplate[ASSIGNMENT_STATISTICS_NAME] = fields.Nested(api.model(ASSIGNMENT_STATISTICS_RESPONSE_TEMPLATE))
# evalGetAll = api.model('evaluator_get', {
#     'status': fields.Integer('0 for success, otherwise there is an error.'),
#     'assigns': fields.Nested(api.model('Assignment evaluator', evalGetTemplate))
# })
addAssignmentEval = api.model('Add Assignment mode', {
    MAIL_FIELD: fields.String('Evaluator mail'),
    ASSIGNMENT_NAME: fields.String('Name of the assignement'),
    ASSIGNMENT_DESCRIPTION: fields.String('Description')
    # I/O

})
addAssignmentParser = api.parser()
addAssignmentParser.add_argument(MAIL_FIELD, type=str, location='form', help='Mail of the evaluator')
addAssignmentParser.add_argument(ASSIGNMENT_NAME, type=str, location='form', help='Name of the assignment.')
addAssignmentParser.add_argument(ASSIGNMENT_DESCRIPTION, type=str, location='form',
                                 help='Description of the assignment')
addAssignmentParser.add_argument(ASSIGNMENT_INPUT_OUTPUTS, action='append', location='form', type=str,
                                 help='List of inputs and output as String, inputs and outputs must be seperated by'
                                      'example where a program has to sum 2 numbers : "8 12 : 20"')
addAssignmentParser.add_argument('assignmentFile', type=datastructures.FileStorage, location='files',
                                 help='Base assignment file.')


@api.route('/evaluator/add', methods=['POST'])
class AddAssignment(Resource):

    @api.expect(addAssignmentParser)
    @token_requiered
    @api.doc(security='apikey', responses={200: 'Assignment added', 422: 'Something is wrong with the data provided',
                                           404: 'Unknow user',
                                           400: 'File missing or type of file not allowed'})
    def post(self):
        """
            Upload new assignment. FORM format : enctype="multipart/form-data"
        """
        requetsArgs = addAssignmentParser.parse_args()
        # print(requetsArgs.get(ASSIGNMENT_DESCRIPTION))
        if not all(requetsArgs[x] is not None for x in requetsArgs): return UNPROCESSABLE_ENTITY_RESPONSE
        eval = getEvalFromMail(requetsArgs.get(MAIL_FIELD))
        if eval is None: return UNKNOW_USER_RESPONSE
        assignID = addAssignment(evalualor=eval, assignName=requetsArgs.get(ASSIGNMENT_NAME),
                                 assignDesc=requetsArgs.get(ASSIGNMENT_DESCRIPTION))
        if requetsArgs.get('assignmentFile') is None: return ASSIGNMENT_FILE_REQUESTED
        try:
            checkAndSaveFile(file=requetsArgs.get('assignmentFile'), assignID=assignID)
            checkAndSaveIOs(ios=requetsArgs.get(ASSIGNMENT_INPUT_OUTPUTS), assignID=assignID)
            # TODO : Check ios/code
            createAssignmentFolder(assignID)
        except FileExtNotAllowed:
            return FILE_TYPE_NOT_ALLOWED
        return BASIC_SUCCESS_RESPONSE


submitProgramParser = api.parser()
submitProgramParser.add_argument(MAIL_FIELD, type=str, location='form', help='Mail of the current user.')
submitProgramParser.add_argument('assignID', type=str, location='form', help='Id of the assignment')
submitProgramParser.add_argument('groupID', type=str, location='form', help='Id of the group related to the assignment')
submitProgramParser.add_argument('assignmentFile', location='files', type=datastructures.FileStorage,
                                 help='File for the assignment')


@api.route('/candidate/submit')
class SubmitAssignmentCandidate(Resource):

    @token_requiered
    @api.doc(security='apikey')
    @api.expect(submitProgramParser)
    def put(self):
        """
            Allows candidate to submit a program for an assignmentpi.payload[apiModels.EVALUATOR_MAIL],
            TODO : Check if already submitted + Launch gradutor
        """
        # Checks token and mail
        now = datetime.now()
        try:
            requetsArgs = submitProgramParser.parse_args()
            if not validateToken(requetsArgs.get(MAIL_FIELD),
                                 request.headers['X-API-KEY']): return MAIL_NOT_MATCHING_TOKEN
            cand = getCanFromMail(requetsArgs.get(MAIL_FIELD).lower())
            if cand is None: return UNKNOW_USER_RESPONSE
            assign = getAssignmentFromId(requetsArgs.get('assignID'))
            if assign is None: return ASSIGNMENT_DOES_NOT_EXIST
            group = getGroupFromId(requetsArgs.get('groupID'))
            if group is None: return GROUP_DOES_NOT_EXIST
            if cand['_id'] not in [candId for candId in
                                   group[GROUPS_CANDIDATES_IDS_FIELD]]: return CANDIDATE_NOT_IN_GROUP
            if not isAssignmnetAssignedToGroup(group[GROUPS_ASSIGNMENTS_FIELD],
                                               assign['_id']): return ASSIGNMENT_NOT_ASSIGNED_TO_GROUP
            if not isFileAllowed(requetsArgs.get('assignmentFile').filename,
                                 ALLOWED_FILES_EXT): return FILE_TYPE_NOT_ALLOWED
            savedFileName = saveSubmissionFile(assignID=str(assign['_id']), candID=str(cand['_id']),
                                               groupID=str(group['_id']),
                                               file=requetsArgs.get('assignmentFile'))
            subID = saveSubmission(assignID=str(assign['_id']), groupID=str(group['_id']), candID=str(cand['_id']),
                                   savedFilename=savedFileName, dateSub=now)
            addSubmissionToGroup(assignID=assign['_id'], subID=subID, groupID=group['_id'])

        except ConnectDatabaseError as e:
            return DATABASE_QUERY_ERROR
        except WrongUserTypeException:
            return WRONG_USER_TYPE


modelEvalGetAll = api.model('model get all assignments for an evaluator', {
    MAIL_FIELD: fields.String('Mail of the user')
})


@api.route('/evaluator/get/all')
class getAllAsignmentEval(Resource):

    @token_requiered
    @api.doc(security='apikey', responses={200: 'Return the list of the assignments that the evaluator created',
                                           503: 'Error while connecting to the databse'})
    def post(self):
        try:
            mail = decodeAuthToken(request.headers['X-API-KEY'])
            eval = getEvalFromMail(mail)
            if eval is None: return UNKNOW_USER_RESPONSE
            assigns = getAllAssignmentsForEval(eval=eval)
            output = formatAssignsForEval(assigns)
            return {'status': 0, 'assignments': output}, 200
        except ConnectDatabaseError:
            return DATABASE_QUERY_ERROR
