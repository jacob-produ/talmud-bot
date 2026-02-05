from core import messages, utils
from school_manager.constants import constants
from school_manager.models.msv_scraping import MSVScraping
from school_manager.models.msv_scraping_inner import MSVScrapingInner
from school_manager.models.institution import Institution
from school_manager.models.student import Student
from school_manager.models.supplier import Supplier
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
GOOGLE_SHEET_NAME = "msv_scraping"
MSV_SCRAPING_CSV_PARAMETER = "msv_scraping_csv"
# MANDATORY_COLUMNS = ["SYMBOL", "INSTITUTION_IDENTITY"]

# msv_scraping table columns
FILE_NAME = "שם הקובץ"
FILE_NUMBER = "מספר קובץ"
INSTITUTION_IDENTITY = "מוסד"
TRANSITION_DATE = "יום ערך"
AMOUNT = "סכום"
NUMBER_OF_TRANSACTIONS = "מספר תנועות"
STATUS = "סטטוס"
UPLOAD_DATE = "מועד העלאה"
REFERENCE_NUMBER = "אסמכתא"
UPLOAD_BY = "הועלה עי"

# msv_scraping_inner table columns
ROW_NUMBER = "מספר שורה"
IDENTITY_NUMBER = "תז"
NAME = "שם"
BANK_DETAILS = "חשבון בנק"
AMOUNT_INNER = "סכום פנימי"
REFERENCE_NUMBER_INNER = "אסמכתא פנימי"

COLS_DTYPES = {
    "מספר קובץ": "int",
    "מוסד": "int",
    "יום ערך": "date",
    "מועד העלאה": "date",
    "סכום": "float",
    "מספר תנועות": "int",
    "אסמכתא": "int",
    "מספר שורה": "int",
    "סכום פנימי": "float",
    "אסמכתא פנימי": "int",
}


def get_bank_details(bank_details):
    bank_details_list = bank_details.split('-')
    branch_number, bank_number, account_number = bank_details_list[0], bank_details_list[1], bank_details_list[2]
    return utils.convert_str_to_int(branch_number), utils.convert_str_to_int(bank_number), \
           utils.convert_str_to_int(account_number)


def get_transactor_id(identity):
    student_id = Student.get_student_by_identity(identity).get('id')
    if student_id is not None:
        return student_id, None
    supplier_id = Supplier.read(many=False, identity=identity).get('id')
    if supplier_id is None:
        raise exceptions.MSVScrapingInnerTransactorNotFoundError(identity)
    return student_id, supplier_id


def create_msv_scraping(row, institution_id, data_source):
    msv_scraping_record = dict(fk_institution_id=institution_id, file_number=row.get(FILE_NUMBER),
                               file_name=row.get(FILE_NAME),institution_number=row.get(INSTITUTION_IDENTITY),
                               transition_date=row.get(TRANSITION_DATE), amount=row.get(AMOUNT),
                               number_of_transaction=row.get(NUMBER_OF_TRANSACTIONS),
                               status=row.get(STATUS),
                               reference_number=row.get(REFERENCE_NUMBER),
                               upload_date=row.get(UPLOAD_DATE),
                               upload_by=row.get(UPLOAD_BY),
                               data_source=data_source)
    msv_scraping = MSVScraping.create(msv_scraping_record)
    if msv_scraping[constants.STR_ERROR]:
        raise exceptions.CreateMSVScrapingError(message=str(msv_scraping[constants.STR_MESSAGE]))
    return msv_scraping[constants.STR_DATA]


def create_msv_scraping_inner(row, msv_scraping_id, branch_number, bank_number, account_number, student_id,
                              supplier_id, data_source):
    msv_scraping_inner_record = dict(fk_msv_scraping_id=msv_scraping_id, row_number=row.get(ROW_NUMBER),
                                     identity=row.get(IDENTITY_NUMBER),
                                     name=row.get(NAME), branch_number=branch_number,
                                     bank_number=bank_number,
                                     account_number=account_number,
                                     reference_number=row.get(REFERENCE_NUMBER_INNER),
                                     amount=row.get(AMOUNT_INNER),
                                     fk_student_id=student_id, fk_supplier_id=supplier_id,
                                     data_source=data_source)
    msv_scraping_inner = MSVScrapingInner.create(msv_scraping_inner_record)
    if msv_scraping_inner[constants.STR_ERROR]:
        raise exceptions.CreateMSVScrapingError(message=str(msv_scraping_inner[constants.STR_MESSAGE]))
    return msv_scraping_inner[constants.STR_DATA]


def create_msv_scraping_from_csv(csv_reader, data_source):
    pop_up_results = []
    scraping_num_of_records, scraping_inner_num_of_records = 0, 0
    scraping_success_records, scraping_inner_success_records = 0, 0
    scraping_errors, scraping_inner_errors = [], []
    current_msv_scraping_id = None
    for row in csv_reader:
        scraping_inner_num_of_records += 1
        try:
            row[UPLOAD_DATE] = row.get(UPLOAD_DATE).replace(',', 'T')
            row[TRANSITION_DATE] = row.get(TRANSITION_DATE).split("(")[0]
            row = utils.convert_csv_row_empty_string_to_none(row)
            row = utils.convert_csv_row_dtype(row, COLS_DTYPES)

            if row.get(INSTITUTION_IDENTITY) is not None:
                scraping_num_of_records += 1
                institution = Institution.get_institution_by_identity(str(row.get(INSTITUTION_IDENTITY)))
                institution_id = institution.get('id')
                if not institution_id:
                    raise exceptions.InstitutionNotExist(row.get(INSTITUTION_IDENTITY))
                msv_scraping = create_msv_scraping(row, institution_id, data_source)
                current_msv_scraping_id = msv_scraping.get('id')
                scraping_success_records += 1
            if current_msv_scraping_id is None:
                raise exceptions.MSVScrapingNotExistError()
            student_id, supplier_id = get_transactor_id(row.get(IDENTITY_NUMBER))
            branch_number, bank_number, account_number = get_bank_details(row.get(BANK_DETAILS))
            create_msv_scraping_inner(row, current_msv_scraping_id, branch_number, bank_number, account_number,
                                      student_id, supplier_id, data_source)
            scraping_inner_success_records += 1
        except (exceptions.InstitutionNotExist, exceptions.CreateMSVScrapingError) as e:
            current_msv_scraping_id = None
            row['error'] = e.message
            scraping_errors.append(row)
        except(exceptions.CreateMSVScrapingInnerError, exceptions.MSVScrapingInnerTransactorNotFoundError) as e:
            row['error'] = e.message
            scraping_inner_errors.append(row)
        except Exception as e:
            row['error'] = str(e)
            scraping_errors.append(row)
    pop_up_results.append(
        popup_utils.get_popup_record(MSVScraping, scraping_num_of_records, scraping_success_records, scraping_errors))
    pop_up_results.append(
        popup_utils.get_popup_record(MSVScrapingInner, scraping_inner_num_of_records, scraping_inner_success_records,
                                     scraping_errors))
    return {constants.STR_MESSAGE: None, constants.STR_ERROR: False, 'popup_results': pop_up_results}


class MSVScrapingAPI(Resource):
    @login_required()
    def get(self):
        if 'csv_template' in request.path:
            try:
                return File.Read.get_csv_template_by_name(MSV_SCRAPING_CSV_PARAMETER)
            except Exception as e:
                print(e)
                return {constants.STR_MESSAGE: messages.REQUEST_FILE_NOT_FOUND_ERROR, constants.STR_ERROR: True}

    @login_required()
    def post(self):
        params = request.form
        if GOOGLE_SHEET_PARAMETER in params and params[GOOGLE_SHEET_PARAMETER]:
            data_source = UPLOAD_SOURCES[1]
            check_reader = get_google_sheet_data(GOOGLE_SHEET_PARAMETER)
            return create_msv_scraping_from_csv(check_reader, data_source)
        elif request.files and MSV_SCRAPING_CSV_PARAMETER in request.files:
            data_source = UPLOAD_SOURCES[0]
            csv_file = request.files[MSV_SCRAPING_CSV_PARAMETER]
            if not csv_file.filename:
                return {constants.STR_MESSAGE: messages.REQUEST_EMPTY_FILE_ERROR, constants.STR_ERROR: True}

            clearing_payments_csv = File.Read.read_file(csv_file.read(),
                                                        csv_file.filename)
            csv_reader = csv.DictReader(clearing_payments_csv)
            return create_msv_scraping_from_csv(csv_reader, data_source)


    @login_required()
    def put(self, branch_id):
        user_json = request.get_json()
        return jsonify(Branch.update(user_json, id=branch_id))


