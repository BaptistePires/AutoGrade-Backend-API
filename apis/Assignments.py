from werkzeug import datastructures
from flask_restplus import Namespace, Resource, fields
from flask import request
from flask_restplus import reqparse
from core.Utils.Constants.ApiResponses import *
import core.Utils.Constants.Constants as generalConsts
from core.Utils.Utils import *
from core.Utils.DatabaseFunctions.UsersFunctions import *

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
parser = api.parser()
parser.add_argument(MAIL_FIELD, type=str, location='form', help='Mail of the evaluator')
parser.add_argument(ASSIGNMENT_NAME, type=str, location='form', help='Name of the assignment.')
parser.add_argument(ASSIGNMENT_DESCRIPTION, type=str, location='form', help='Description of the assignment')
parser.add_argument(ASSIGNMENT_DEADLINE, type=str, location='form', help='Deadline, date format must be : YYYY/MM/dd %H:%M:%S')
parser.add_argument('assignmentFile', type=datastructures.FileStorage, location='files', help='Base assignment file.')



@api.route('/test', methods=['POST'])
class AddAssignment(Resource):

    @api.expect(parser)
    @token_requiered
    @api.doc(security='apikey')
    def post(self):
        """
            Upload new assignment. FORM format : enctype="multipart/form-data"
        """
        requetsArgs = parser.parse_args()
        if not all(requetsArgs[x] is not None for x in requetsArgs): return UNPROCESSABLE_ENTITY_RESPONSE
        eval = getEvalFromMail(requetsArgs.get(MAIL_FIELD))
        if eval is None: return UNKNOW_USER_RESPONSE
        date = datetime.datetime.strptime(requetsArgs[ASSIGNMENT_DEADLINE], "%Y/%m/%d %H:%M:%S")
        if not isDateBeforeNow(date): return UNPROCESSABLE_ENTITY_RESPONSE # If date is before now

        assigmentFile = requetsArgs.get('assignmentFile')
        if assigmentFile is None: return ASSIGNMENT_FILE_REQUESTED
        if not isFileAllowed(assigmentFile.filename, generalConsts.ALLOWED_FILES_EXT): return FILE_TYPE_NOT_ALLOWED
        saveFileName = generalConsts.BASE_FILE_NAME + '.' +getFileExt(assigmentFile.filename)

