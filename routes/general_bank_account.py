from flask import  jsonify
from school_manager.routes.auth import login_required

import csv,sys
from core import messages, utils
from flask import request
from flask_restful import Resource
from school_manager.constants import constants

from school_manager.modules.file.file import File

from school_manager.modules.constants_validation import ConstantsValidation
from school_manager.modules import exceptions
from school_manager.modules import popup_utils

from school_manager.models.general_bank_account import GeneralBankAccount

from school_manager.models.student import Student
from school_manager.models.employee import Employee
from school_manager.models.supplier import Supplier
from school_manager.models.donator import Donator

from school_manager.constants.constants_lists import UPLOAD_SOURCES


GENERAL_BANK_ACCOUNT_CSV_PARAMETER = "general_bank_account_csv"

BANK_NUMBER_COL = "מספר בנק"
BRANCH_NUMBER_COL = "מספר סניף"
ACCOUNT_NUMBER_COL = "מספר חשבון"
ATTRIBUTION_IDENTITY_COL = "תעודת זהות"
STATUS = "סטטוס"

def convert_empty_string_to_null(col_val):
    return col_val if col_val else None

def convert_string_to_int(string):
    try:
        return int(float(string))
    except ValueError as e:
        print(e)
        return None

def constants_validation(row):
    ConstantsValidation.general_bank_account_status_validation(row[STATUS])

def create_general_bank_account(row, attribution, data_source):
    attribution_identity = convert_string_to_int(row.get(ATTRIBUTION_IDENTITY_COL))
    attribution_id = getattr(sys.modules[__name__], attribution.capitalize()) \
        .read(only_columns_list=['id'], many=False, identity=str(attribution_identity)).get('id')


    general_ba_dict = dict(bank_number=convert_empty_string_to_null(row[BANK_NUMBER_COL]),
                           status=convert_empty_string_to_null(row[STATUS]),
                           account_number=convert_empty_string_to_null(row[ACCOUNT_NUMBER_COL]),
                           branch_number=convert_empty_string_to_null(row[BRANCH_NUMBER_COL]),
                           data_source=data_source)
    attribution_dict = {f'fk_{attribution}_id': attribution_id}
    general_ba_dict = {**general_ba_dict, **attribution_dict}

    general_bank_account = GeneralBankAccount.create(general_ba_dict)
    if general_bank_account[constants.STR_ERROR]:
        raise exceptions.CreateGeneralBankAccountError(
            message=str(general_bank_account[constants.STR_MESSAGE]))
    return general_bank_account[constants.STR_DATA]

def create_general_ba_from_csv(csv_reader, attribution,data_source):
    pop_up_results = []
    num_of_records, general_ba_success_records = 0, 0
    constants_errors, general_ba_errors = [], []
    for row in csv_reader:
        try:
            num_of_records += 1
            row = utils.convert_csv_row_empty_string_to_none(row)

            general_bank_account = create_general_bank_account(row, attribution, data_source)
            general_ba_success_records += 1
        except exceptions.ConstantNotFound as e:
            row['error'] = str(e)
            general_ba_errors.append(row)
        except exceptions.CreateGeneralBankAccountError as e:
            row['error'] = e.message
            general_ba_errors.append(row)
    pop_up_results.append(
        popup_utils.get_popup_record(GeneralBankAccount, num_of_records, general_ba_success_records,
                                     general_ba_errors))

    return {constants.STR_MESSAGE: None, constants.STR_ERROR: False, 'popup_results': pop_up_results}







class GeneralBankAccountAPI(Resource):
    @staticmethod
    @login_required()
    def get(general_bank_account_id=None):
        if 'csv_template' in request.path:
            try:
                return File.Read.get_csv_template_by_name(GENERAL_BANK_ACCOUNT_CSV_PARAMETER)
            except Exception as e:
                print(e)
                return {constants.STR_MESSAGE: messages.REQUEST_FILE_NOT_FOUND_ERROR, constants.STR_ERROR: True}

        if general_bank_account_id:
            results = GeneralBankAccount.read(many=False, id=general_bank_account_id)
        else:
            results = GeneralBankAccount.read()
        return jsonify(results)

    @staticmethod
    @login_required()
    def post():
        if request.files and GENERAL_BANK_ACCOUNT_CSV_PARAMETER in request.files:

            csv_file = request.files[GENERAL_BANK_ACCOUNT_CSV_PARAMETER]
            if not csv_file.filename:
                return {constants.STR_MESSAGE: messages.REQUEST_EMPTY_FILE_ERROR, constants.STR_ERROR: True}
            params = request.form
            if 'attribution' not in params:
                return {constants.STR_MESSAGE: messages.REQUEST_WRONG_FORM_PARAMETERS, constants.STR_ERROR: True}

            attribution = params['attribution']
            csv_data = File.Read.read_file(csv_file.read(), csv_file.filename)
            csv_reader = csv.DictReader(csv_data)
            data_source = UPLOAD_SOURCES[0]
            return create_general_ba_from_csv(csv_reader, attribution=attribution, data_source=data_source )
        else:
            general_bank_account_json = request.get_json()
            return jsonify(GeneralBankAccount.create(general_bank_account_json))

    @staticmethod
    @login_required()
    def put(general_bank_account_id):
        general_bank_account_json = request.get_json()
        return jsonify(GeneralBankAccount.update(general_bank_account_json, id=general_bank_account_id))

    @staticmethod
    @login_required()
    def delete(general_bank_account_id):
        return jsonify(GeneralBankAccount.delete(id=general_bank_account_id))

