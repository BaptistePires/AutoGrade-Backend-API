from werkzeug import datastructures
from flask_restplus import Namespace, Resource, fields
from flask import request
from flask_restplus import reqparse
from core.Utils.Constants.ApiResponses import *
import core.Utils.Constants.Constants as generalConsts
from core.Utils.DatabaseFunctions.AssignmentsFunctions import addAssignment, getAllAssignmentsForEval
from core.Utils.Exceptions import ConnectDatabaseError
from core.Utils.Utils import *
from core.Utils.DatabaseFunctions.UsersFunctions import *
from os.path import join
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
addAssignmentParser.add_argument(MAIL_FIELD, type=str, location='form', help='Mail of the evaluator')
addAssignmentParser.add_argument(ASSIGNMENT_NAME, type=str, location='form', help='Name of the assignment.')
addAssignmentParser.add_argument(ASSIGNMENT_DESCRIPTION, type=str, location='form',
                                 help='Description of the assignment')
addAssignmentParser.add_argument(ASSIGNMENT_DEADLINE, type=str, location='form',
                                 help='Deadline, date format must be : YYYY/MM/dd %H:%M:%S')
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
        if not all(requetsArgs[x] is not None for x in requetsArgs): return UNPROCESSABLE_ENTITY_RESPONSE
        eval = getEvalFromMail(requetsArgs.get(MAIL_FIELD))
        if eval is None: return UNKNOW_USER_RESPONSE
        date = datetime.datetime.strptime(requetsArgs[ASSIGNMENT_DEADLINE], "%Y/%m/%d %H:%M:%S")
        if not isDateBeforeNow(date): return UNPROCESSABLE_ENTITY_RESPONSE  # If date is before now
        assignID = addAssignment(evalualor=eval, assignName=requetsArgs.get(ASSIGNMENT_NAME), assignDeadLine=date,
                                 assignDesc=requetsArgs.get(ASSIGNMENT_DESCRIPTION))
        if requetsArgs.get('assignmentFile') is None: return ASSIGNMENT_FILE_REQUESTED
        try:
            checkAndSaveFile(file=requetsArgs.get('assignmentFile'), assignID=assignID)
            checkAndSaveIOs(ios=requetsArgs.get(ASSIGNMENT_INPUT_OUTPUTS), assignID=assignID)
            # TODO : Check ios/code
        except FileExtNotAllowed:
            return FILE_TYPE_NOT_ALLOWED
        return BASIC_SUCCESS_RESPONSE

submitProgramParser = api.parser()

@api.route('/candidate/submit')
class SubmitAssignmentCandidate(Resource):


    @token_requiered
    @api.doc(security='apikey')
    def post(self):
        """
            Allows candidate to submit a program for an assignment
        """
        pass

modelEvalGetAll = api.model('model get all assignments for an evaluator', {
    MAIL_FIELD: fields.String('Mail of the user')
})

@api.route('/evaluator/get/all')
class getAllAsignmentEval(Resource):

    @api.expect(modelEvalGetAll)
    @token_requiered
    @api.doc(security='apikey',  responses=  {200: 'Return the list of the assignments that the evaluator created'
                                              503: 'Error while connecting to the databse'})
    def post(self):
        try:
            eval = getEvalFromMail(api.payload.get(MAIL_FIELD))
            if eval is None: return UNKNOW_USER_RESPONSE
            assigns = getAllAssignmentsForEval(eval=eval)
        except ConnectDatabaseError:
            return DATABASE_QUERY_ERROR
        return {'status': 0, 'assignments': assigns}, 200