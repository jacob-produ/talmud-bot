import csv

from core import messages, utils
from flask import request, jsonify
from flask_restful import Resource
from school_manager.constants import constants
from school_manager.modules import exceptions
from school_manager.modules.file.file import File
from school_manager.modules import popup_utils

from school_manager.models.institution import Institution
from school_manager.models.bank_account import BankAccount
from school_manager.constants.constants import UT8_WITH_BOM_ENCODING
from school_manager.routes.auth import login_required

from school_manager.modules.google_sheet import get_google_sheet_data

from school_manager.constants.constants_lists import UPLOAD_SOURCES

GOOGLE_SHEET_PARAMETER = "google_sheet"
GOOGLE_SHEET_NAME = "institution_bank_account"
INSTITUTION_BANK_ACCOUNT_CSV_PARAMETER = "institution_bank_account_csv"

INSTITUTION_NAME = "שם מוסד"
INSTITUTION_SHORT_NAME = "שם מוסד מקוצר"
INSTITUTION_IDENTITY = "זהות המוסד"
INSTITUTION_MSV_INSTITUTE_CODE = "קוד מסב חיוב"
INSTITUTION_MSV_SENDING_INSTITUTE_CODE = "קוד מסב זיכוי (sending)"
INSTITUTION_CITY = "עיר המוסד"
INSTITUTION_ZIP_CODE = "מיקוד המוסד"
INSTITUTION_PHONE_NUMBER = "טלפון המוסד"
INSTITUTION_CAPACITY = "יתרת מכסה"

BANK_ACCOUNT_BANK_NUMBER = "מספר בנק"
BANK_ACCOUNT_BRANCH_NAME = "שם סניף"
BANK_ACCOUNT_BRANCH_NUMBER = "מספר סניף"
BANK_ACCOUNT_NUMBER = "מספר חשבון בנק"
BANK_ACCOUNT_PREV_NUMBER = "מספר חושבון בנק קודם"
BANK_ACCOUNT_CITY = "עיר חשבון בנק"
BANK_ACCOUNT_STREET = "רחוב חשבון בנק"
BANK_ACCOUNT_STREET_NUMBER = "מספר רחוב סניף"
BANK_ACCOUNT_USERNAME = "שם משתמש סניף"
BANK_ACCOUNT_PASSWORD = "סיסמא סניף"
BANK_ACCOUNT_SIGNATURE_IMAGE = "תצלום חתימה סניף"
BANK_ACCOUNT_LINE_OF_CREDIT = "מסגרת אשראי סניף"
BANK_ACCOUNT_PHONE_NUMBER = "טלפון חשבון בנק"


def create_institution(row, data_source):
    institution_identity = row.get(INSTITUTION_IDENTITY)
    institution = Institution.get_institution_by_identity(institution_identity)
    if institution:
        return institution

    institution_name, institution_short_name = row.get(
        INSTITUTION_NAME), row.get(INSTITUTION_SHORT_NAME)
    institution_msv_institute_code, institution_msv_sending_institute_code = row.get(
        INSTITUTION_MSV_INSTITUTE_CODE), row.get(INSTITUTION_MSV_SENDING_INSTITUTE_CODE)
    institution_city, institution_zip_code, institution_phone_number = row.get(INSTITUTION_CITY), row.get(
        INSTITUTION_ZIP_CODE), row.get(INSTITUTION_PHONE_NUMBER)
    institution_capacity = row.get(INSTITUTION_CAPACITY)
    institution_record = dict(identity=institution_identity, name=institution_name,
                              short_name=institution_short_name,
                              msv_institute_code=institution_msv_institute_code,
                              msv_sending_institute_code=institution_msv_sending_institute_code,
                              city=institution_city, zip_code=institution_zip_code,
                              phone_number=institution_phone_number,
                              capacity=institution_capacity,
                              data_source=data_source)
    institution = Institution.create(institution_record)
    if institution[constants.STR_ERROR]:
        raise exceptions.CreateInstitutionError(identity=institution_identity,
                                                message=str(institution[constants.STR_MESSAGE]))
    return institution[constants.STR_DATA]


def create_bank_account(row, institution_id, data_source):
    ba_bank_number, ba_branch_name, ba_branch_number = row.get(BANK_ACCOUNT_BANK_NUMBER), row.get(
        BANK_ACCOUNT_BRANCH_NAME), row.get(BANK_ACCOUNT_BRANCH_NUMBER)
    ba_account_number, ba_prev_account_number = row.get(BANK_ACCOUNT_NUMBER), row.get(BANK_ACCOUNT_PREV_NUMBER)
    ba_city, ba_street, ba_street_number = row.get(BANK_ACCOUNT_CITY), row.get(BANK_ACCOUNT_STREET), row.get(
        BANK_ACCOUNT_STREET_NUMBER)
    ba_username, ba_password = row.get(BANK_ACCOUNT_USERNAME), row.get(BANK_ACCOUNT_PASSWORD)
    ba_signature_image, ba_line_of_credit = row.get(BANK_ACCOUNT_SIGNATURE_IMAGE), row.get(BANK_ACCOUNT_LINE_OF_CREDIT)
    ba_phone_number = row.get(BANK_ACCOUNT_PHONE_NUMBER)
    bank_account_record = dict(bank_number=ba_bank_number, branch_name=ba_branch_name, branch_number=ba_branch_number,
                               account_number=ba_account_number, prev_account_number=ba_prev_account_number,
                               city=ba_city, street=ba_street, street_number=ba_street_number,
                               username=ba_username, password=ba_password,
                               phone_number=ba_phone_number, line_of_credit=ba_line_of_credit,
                               fk_institution_id=institution_id, data_source=data_source)
    bank_account = BankAccount.create(bank_account_record)
    if bank_account[constants.STR_ERROR]:
        raise exceptions.CreateBankAccountError(number=ba_bank_number, message=str(bank_account[constants.STR_MESSAGE]))
    return bank_account[constants.STR_DATA]


def create_institution_bank_account_from_csv(csv_reader, data_source):
    pop_up_results = []
    num_of_records, institution_success_records, bank_account_success_records = 0, 0, 0
    institution_errors, bank_account_errors = [], []
    for row in csv_reader:
        num_of_records += 1
        try:
            row = utils.convert_csv_row_empty_string_to_none(row)

            institution = create_institution(row, data_source)
            institution_success_records += 1

            bank_account = create_bank_account(row, institution.get('id'), data_source)
            bank_account_success_records += 1
        except exceptions.CreateInstitutionError as e:
            row['error'] = e.message
            institution_errors.append(row)
        except exceptions.CreateBankAccountError as e:
            row['error'] = e.message
            bank_account_errors.append(row)

    pop_up_results.append(
        popup_utils.get_popup_record(Institution, num_of_records, institution_success_records, institution_errors))
    pop_up_results.append(
        popup_utils.get_popup_record(BankAccount, num_of_records, bank_account_success_records, bank_account_errors))

    return {constants.STR_MESSAGE: None, constants.STR_ERROR: False, 'popup_results': pop_up_results}
    return BankAccount.create_ignore(bank_accounts)


class InstitutionBankAccountAPI(Resource):
    @staticmethod
    @login_required()
    def get():
        if 'csv_template' in request.path:
            try:
                return File.Read.get_csv_template_by_name(INSTITUTION_BANK_ACCOUNT_CSV_PARAMETER)
            except Exception as e:
                print(e)
                return {constants.STR_MESSAGE: messages.REQUEST_FILE_NOT_FOUND_ERROR, constants.STR_ERROR: True}

    @staticmethod
    @login_required()
    def post():
        # Add from csv file
        params = request.form
        if GOOGLE_SHEET_PARAMETER in params and params[GOOGLE_SHEET_PARAMETER]:
            print('here')
            check_reader = get_google_sheet_data(GOOGLE_SHEET_PARAMETER)
            data_source = UPLOAD_SOURCES[1]
            return create_institution_bank_account_from_csv(check_reader, data_source)
        elif request.files and INSTITUTION_BANK_ACCOUNT_CSV_PARAMETER in request.files:
            data_source = UPLOAD_SOURCES[0]
            file = request.files[INSTITUTION_BANK_ACCOUNT_CSV_PARAMETER]
            if not file.filename:
                return {constants.STR_MESSAGE: messages.REQUEST_EMPTY_FILE_ERROR, constants.STR_ERROR: True}
            csv_data = File.Read.read_file(file.read(), file.filename)
            check_reader = csv.DictReader(csv_data)

            return create_institution_bank_account_from_csv(check_reader, data_source)

        return {constants.STR_MESSAGE: messages.REQUEST_EMPTY_FILE_ERROR, constants.STR_ERROR: True}
