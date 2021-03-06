from werkzeug import datastructures
from flask_restplus import Namespace, Resource, fields, marshal_with
from flask import request, send_from_directory
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
from subprocess import Popen
import platform

import json

api = Namespace('Assignments', description="Assignments related operations.")
##############
# API models #
##############
addAssignmentEval = api.model('Add Assignment mode', {
    MAIL_FIELD: fields.String('Evaluator mail'),
    ASSIGNMENT_NAME: fields.String('Name of the assignement'),
    ASSIGNMENT_DESCRIPTION: fields.String('Description')
    # I/O

})
addAssignmentParser = api.parser()
addAssignmentParser.add_argument(ASSIGNMENT_NAME, type=str, location='form', help='Name of the assignment.')
addAssignmentParser.add_argument(ASSIGNMENT_DESCRIPTION, type=str, location='form',
                                 help='Description of the assignment')
addAssignmentParser.add_argument(ASSIGNMENT_INPUT_OUTPUTS, action='append', location='form', type=str,
                                 help='List of inputs and output as String, inputs and outputs must be seperated by'
                                      'example where a program has to sum 2 numbers : "8 12 : 20"')
addAssignmentParser.add_argument('assignmentFile', type=datastructures.FileStorage, location='files',
                                 help='Base assignment file.')
addAssignmentParser.add_argument(ASSIGNMENT_MARKING_SCHEME_NAME + '_' + ASSIGNMENT_FILE_SIZE, type=str,
                                 help='Marking schame for the file size')
addAssignmentParser.add_argument(ASSIGNMENT_MARKING_SCHEME_NAME + '_' + ASSIGNMENT_STAT_TIME, type=str,
                                 help='Marking schame for the cpu time used')
addAssignmentParser.add_argument(ASSIGNMENT_MARKING_SCHEME_NAME + '_' + ASSIGNMENT_MEMORY_USED, type=str,
                                 help='Marking schame for the memory used')


@api.route('/evaluator/create', methods=['POST'])
class AddAssignment(Resource):
    POST_FIELDS = [field.name for field in addAssignmentParser.args]

    @api.expect(addAssignmentParser)
    @token_requiered
    @api.doc(security='apikey', responses={200: 'Assignment added', 422: 'Something is wrong with the data provided',
                                           404: 'Unknow user',
                                           400: 'File missing or type of file not allowed'})
    def post(self):
        """
            Upload new assignment.
            FORM format : enctype="multipart/form-data".
            This route add an assignment to the list of assignments of the current evaluator. After you added an
            assignment, you can add it by its ID to a group.
            The sum of three marking schemes HAS to be 100.
        """

        requetsArgs = addAssignmentParser.parse_args()
        print(requetsArgs)
        # print(requetsArgs.get(ASSIGNMENT_DESCRIPTION))
        if not all(requetsArgs[x] is not None or x not in self.POST_FIELDS for x in requetsArgs):
            return UNPROCESSABLE_ENTITY_RESPONSE

        mail = decodeAuthToken(request.headers['X-API-KEY'])
        eval = getEvalFromMail(mail)
        if eval is None: return UNKNOWN_USER_RESPONSE

        try:
            file = requetsArgs.get('assignmentFile')
            if not isFileAllowed(file.filename, ALLOWED_FILES_EXT): return FILE_TYPE_NOT_ALLOWED
            markingScheme = checkAndFormatMarkingSchemRqstArgs(requetsArgs)
            assignID = addAssignment(evalualor=eval, assignName=requetsArgs.get(ASSIGNMENT_NAME),
                                     assignDesc=requetsArgs.get(ASSIGNMENT_DESCRIPTION), markingScheme=markingScheme,
                                     originalFilename=requetsArgs.get('assignmentFile').filename)
            checkAndSaveFile(file=requetsArgs.get('assignmentFile'), assignID=assignID)
            checkAndSaveIOs(ios=requetsArgs.get(ASSIGNMENT_INPUT_OUTPUTS), assignID=assignID)
            if requetsArgs.get('assignmentFile') is None: return ASSIGNMENT_FILE_REQUESTED
            createAssignmentFolder(assignID)
            if platform.platform().lower().startswith('linux'):
                from os import getcwd
                print(getcwd())
                Popen(['python3', 'AutoGrade/AutoGrade.py', '-ch', ASSIGNMENTS_FOLDER_FULL_PATH, str(assignID)])
            return {'status': 0, 'assign_id': str(assignID)}
        except FileExtNotAllowed:
            return FILE_TYPE_NOT_ALLOWED
        except WrongMarkingScheme:
            return WRONG_MARKING_SCHEME


submitProgramParser = api.parser()
submitProgramParser.add_argument('assignID', type=str, location='form', help='Id of the assignment')
submitProgramParser.add_argument('groupID', type=str, location='form', help='Id of the group related to the assignment')
submitProgramParser.add_argument('assignmentFile', location='files', type=datastructures.FileStorage,
                                 help='File for the assignment')


@api.route('/candidate/submit')
class SubmitAssignmentCandidate(Resource):
    POST_FIELDS = [field.name for field in submitProgramParser.args]

    @token_requiered
    @api.doc(security='apikey')
    @api.expect(submitProgramParser)
    def post(self):
        """
            Submit a program to an assignment as a candidate.
            This route allows candidates to submit their program to a group assignment.
            TODO : Check if already submitted + Launch gradutor
        """
        mail = decodeAuthToken(request.headers['X-API-KEY'])
        requetsArgs = submitProgramParser.parse_args()
        if not all(requetsArgs[x] is not None or x not in self.POST_FIELDS for x in requetsArgs):
            return UNPROCESSABLE_ENTITY_RESPONSE
        now = datetime.now().timestamp()
        try:
            cand = getCandidateFromMail(mail.lower())
            if cand is None: return UNKNOWN_USER_RESPONSE
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
                                   savedFilename=savedFileName, dateSub=now,
                                   originalFilename=requetsArgs.get('assignmentFile').filename)
            addSubmissionToGroup(assignID=assign['_id'], subID=subID, groupID=group['_id'])

            if platform.platform().lower().startswith('linux') and isCorrectionAllowed(group[GROUPS_ID_EVAL_FIELD]):
                decrEvalCorrectionsAllowedFromID(group[GROUPS_ID_EVAL_FIELD])
                Popen(['python3', 'AutoGrade/AutoGrade.py', '-cs', GROUPS_DIR_PATH, str(subID)])

            return {'status': 0, 'submission_id': str(subID)}
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
    def get(self):
        """
            Get all assignment that the current evaluator created.
        """
        try:
            mail = decodeAuthToken(request.headers['X-API-KEY'])
            eval = getEvalFromMail(mail)
            if eval is None: return UNKNOWN_USER_RESPONSE
            assigns = getAllAssignmentsForEval(eval=eval)
            output = formatAssignsWithoutSubmissionsForEval(assigns)
            return {'status': 0, 'assignments': output}, 200
        except ConnectDatabaseError:
            return DATABASE_QUERY_ERROR
        except WrongUserTypeException:
            return WRONG_USER_TYPE


@api.route('/candidate/get/all')
class GetAllAssignmentsCandidate(Resource):

    @token_requiered
    @api.doc(security='apikey', responses={
        200: str({'status': 0,
                  'submissions': '{ "id": "5e382c00affe678e8137785e", "grade": null,"deadline": 900000000000000,'
                                 '"group": {"id": "5e3823d7316052a477f800a1","name": "string"}'})
    })
    def get(self):
        mail = decodeAuthToken(request.headers['X-API-KEY'])
        try:
            candidate = getCandidateFromMail(mail)
            submissions = formatSubmissionsForCand(candidate['_id'])
            return {'status': 0, 'submissions': submissions}
        except ConnectDatabaseError:
            return DATABASE_QUERY_ERROR
        except WrongUserTypeException:
            return WRONG_USER_TYPE

@api.route('/candidate/get/submission/file/<string:submission_id>')
class GetSubmissionFile(Resource):

    @token_requiered
    @api.doc(security='apikey')
    def get(self, submission_id):
        mail = decodeAuthToken(request.headers['X-API-KEY'])
        user = getOneUserByMail(mail)
        if user is None: return UNKNOWN_USER_RESPONSE
        submission = getSubmissionFromID(submission_id)
        if submission is None: return {'status': -1, 'error': 'Submission does not exists'}, 404
        path = GROUPS_DIR_PATH + sep + str(submission[ASSIGNMENT_SUB_GROUP_ID]) + sep + str(submission[ASSIGNMENT_SUB_ASSIGN_ID])
        return send_from_directory(path, submission[ASSIGNMENT_FILENAME])

@api.route('/evaluator/get/assignment/file/<string:assignment_id>')
class GetSubmissionFile(Resource):

    @token_requiered
    @api.doc(security='apikey')
    def get(self, assignment_id):
        mail = decodeAuthToken(request.headers['X-API-KEY'])
        evaluator = getEvalFromMail(mail)
        if evaluator is None: return UNKNOWN_USER_RESPONSE
        assignment = getAssignmentFromId(assignment_id)
        if assignment is None: return {'status': -1, 'error': 'Submission does not exists'}, 404
        path = ASSIGNMENTS_FOLDER_FULL_PATH + sep + str(assignment_id)
        return send_from_directory(path, assignment[ASSIGNMENT_FILENAME])

