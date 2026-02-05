from core import messages, utils
from school_manager.constants import constants
from school_manager.models.branch import Branch
from school_manager.models.institution import Institution
from flask import request, jsonify, Response
from flask_restful import Resource
from school_manager.routes.auth import login_required, role_required

from school_manager.modules.file.file import File
from school_manager.modules import exceptions
from school_manager.modules import popup_utils
import csv

from school_manager.modules.google_sheet import get_google_sheet_data

from school_manager.constants.constants_lists import UPLOAD_SOURCES

GOOGLE_SHEET_PARAMETER = "google_sheet"
GOOGLE_SHEET_NAME = "branch"
BRANCH_CSV_PARAMETER = "branch_csv"
MANDATORY_COLUMNS = ["SYMBOL", "INSTITUTION_IDENTITY"]

SYMBOL = "סמל הסניף"
INSTITUTION_IDENTITY = "מוסד הסניף"
CITY = "עיר"
STREET = "רחוב"
STREET_NUMBER = "מספר בית"
START_DATE = "תאריך התחלה"
FIRST_OPENING_HOUR = "תחילת שעת פעילות ראשונה"
FIRST_CLOSING_HOUR = "סוף שעת פעילות ראשונה"
SECOND_OPENING_HOUR = "תחילת שעת פעילות שנייה"
SECOND_CLOSING_HOUR = "סוף שעת פעילות שנייה"
SHIFT_MANAGER_FIRST_NAME = "שם פרטי אחראי"
SHIFT_MANAGER_LAST_NAME = "שם משפחה אחראי"
FIRST_CONTACT_NAME = "שם איש קשר ראשון"
SECOND_CONTACT_NAME = "שם איש קשר שני"
FIRST_CONTACT_PHONE = "טלפון איש קשר ראשון"
SECOND_CONTACT_PHONE = "טלפון איש קשר שני"
COMMENTS = "הערות"
SCHOOL_DESCRIPTION = "תיאור מקום לימודים"

COLS_DTYPES = {
    "תז": "string",
    "פרמיהחודשית": "float",
    "חודשנוכחי": "date",
    "סוגלימוד": "int",
}

def create_branch(row, institution_id, data_source):
    start_date = row.get(START_DATE) if row.get(START_DATE) else None
    # start_date = None
    symbol = int(float(row.get(SYMBOL))) if row.get(SYMBOL) else None
    branch_record = dict(fk_institution_id=institution_id, symbol=symbol, city=row.get(CITY),
                         street=row.get(STREET),
                         street_number=row.get(STREET_NUMBER), start_date=start_date,
                         first_opening_hour=row.get(FIRST_OPENING_HOUR),
                         first_closing_hour=row.get(FIRST_CLOSING_HOUR),
                         second_opening_hour=row.get(SECOND_OPENING_HOUR),
                         second_closing_hour=row.get(SECOND_CLOSING_HOUR),
                         shift_manager_first_name=row.get(SHIFT_MANAGER_FIRST_NAME),
                         shift_manager_last_name=row.get(SHIFT_MANAGER_LAST_NAME),
                         first_contact_name=row.get(FIRST_CONTACT_NAME),
                         second_contact_name=row.get(SECOND_CONTACT_NAME),
                         first_contact_phone=row.get(FIRST_CONTACT_PHONE),
                         second_contact_phone=row.get(SECOND_CONTACT_PHONE), comments=row.get(COMMENTS),
                         school_description=row.get(SCHOOL_DESCRIPTION),
                         data_source=data_source)
    branch = Branch.create(branch_record)
    if branch[constants.STR_ERROR]:
        raise exceptions.CreateBranchError(message=str(branch[constants.STR_MESSAGE]))
    return branch[constants.STR_DATA]



def create_branches_from_csv(csv_reader, data_source):
    pop_up_results = []
    num_of_records, branch_success_records = 0, 0
    branch_errors = []
    for row in csv_reader:
        num_of_records += 1
        try:
            row = utils.convert_csv_row_empty_string_to_none(row)
            institution = Institution.get_institution_by_identity(row.get(INSTITUTION_IDENTITY))
            institution_id = institution.get('id')
            if not institution_id:
                raise exceptions.InstitutionNotExist(row.get(INSTITUTION_IDENTITY))
            branch = create_branch(row, institution_id, data_source)

            branch_success_records += 1
        except (exceptions.InstitutionNotExist,exceptions.CreateBranchError) as e:
            row['error'] = e.message
            branch_errors.append(row)
        except Exception as e:
            row['error'] = str(e)
            branch_errors.append(row)
    pop_up_results.append(
        popup_utils.get_popup_record(Branch, num_of_records, branch_success_records, branch_errors))
    return {constants.STR_MESSAGE: None, constants.STR_ERROR: False, 'popup_results': pop_up_results}


class BranchAPI(Resource):
    @login_required()
    def get(self, branch_id=None):
        if 'csv_template' in request.path:
            try:
                return File.Read.get_csv_template_by_name(BRANCH_CSV_PARAMETER)
            except Exception as e:
                print(e)
                return {constants.STR_MESSAGE: messages.REQUEST_FILE_NOT_FOUND_ERROR, constants.STR_ERROR: True}
        if branch_id:
            results = Branch.read(many=False, id=branch_id)
        else:
            results = Branch.read()
        return jsonify(results)

    @login_required()
    def post(self):
        params = request.form
        if GOOGLE_SHEET_PARAMETER in params and params[GOOGLE_SHEET_PARAMETER]:
            data_source = UPLOAD_SOURCES[1]
            print('here')
            check_reader = get_google_sheet_data(GOOGLE_SHEET_PARAMETER)
            return create_branches_from_csv(check_reader,data_source)
        elif request.files and BRANCH_CSV_PARAMETER in request.files:
            data_source = UPLOAD_SOURCES[0]
            clearing_payments_csv_file = request.files[BRANCH_CSV_PARAMETER]
            if not clearing_payments_csv_file.filename:
                return {constants.STR_MESSAGE: messages.REQUEST_EMPTY_FILE_ERROR, constants.STR_ERROR: True}

            clearing_payments_csv = File.Read.read_file(clearing_payments_csv_file.read(),
                                                        clearing_payments_csv_file.filename)
            csv_reader = csv.DictReader(clearing_payments_csv)
            return create_branches_from_csv(csv_reader, data_source)

        branch_json = request.get_json()
        return jsonify(Branch.create(branch_json))

    @login_required()
    def put(self, branch_id):
        user_json = request.get_json()
        return jsonify(Branch.update(user_json, id=branch_id))

    @login_required()
    def delete(self, branch_id):
        result = Branch.delete(id=branch_id)

        if result[constants.STR_ERROR]:
            return jsonify({constants.STR_ERROR: True
                               , constants.STR_MESSAGE: messages.COLUMN_DELETE_FAILED.format("Branch")})

        return jsonify({constants.STR_ERROR: False
                           , constants.STR_MESSAGE: messages.COLUMN_DELETE_SUCCESSFULLY.format("Branch")})
