import csv
from core import messages, utils
from flask_restful import Resource
from school_manager.constants import constants
from flask import request, jsonify
from school_manager.models.bank_account import BankAccount
from school_manager.models.trend_coordinator import TrendCoordinator
from school_manager.routes.auth import login_required
from school_manager.models.clearing_platform import ClearingPlatform
from school_manager.modules.file.file import File

from school_manager.modules import exceptions
from school_manager.modules import popup_utils

from school_manager.constants.constants_lists import UPLOAD_SOURCES

CLEARING_PLATFORM_CSV_PARAMETER = 'clearing_platform_csv'

NAME = "שם"
BANK_ACCOUNT_NUMBER = "מספר חשבון"
TREND_COORDINATOR_NAME = "שם מנחה"


def get_bank_account_institution_id(account_number):
    bank_account_record = BankAccount.read(['id', 'fk_institution_id'], many=False, account_number=account_number)
    return bank_account_record.get('id'), bank_account_record.get('fk_institution_id')

def create_clearing_platform(row,main_trend_coordinator_id, data_source):
    bank_account_id, trend_coordinator_id = None, None
    platform_name = row.get(NAME, '')
    bank_account_number = row.get(BANK_ACCOUNT_NUMBER, '')
    trend_coordinator_name = row.get(TREND_COORDINATOR_NAME, '')
    if bank_account_number:
        bank_account_id = BankAccount.read(many=False, account_number=bank_account_number).get('id')
    if main_trend_coordinator_id:
        trend_coordinator_id = main_trend_coordinator_id
    elif trend_coordinator_name:
        trend_coordinator_id = TrendCoordinator.get_trend_coordinator_by_name(name=trend_coordinator_name,
                                                                              many=False).get('id')

    platform_dict = dict(name=platform_name, fk_bank_account_id=bank_account_id,
                         fk_trend_coordinator_id=trend_coordinator_id,
                         data_source=data_source)
    clearing_platform = ClearingPlatform.create(platform_dict)
    if clearing_platform[constants.STR_ERROR]:
        raise exceptions.CreateClearingPlatformError(
            message=str(clearing_platform[constants.STR_MESSAGE]))
    return clearing_platform[constants.STR_DATA]

def create_clearing_platform_from_csv(csv_reader, data_source, main_trend_coordinator_id=None):
    pop_up_results = []
    num_of_records, clearing_platform_success_records = 0, 0
    constants_errors, clearing_platform_errors = [], []
    for row in csv_reader:
        try:
            num_of_records += 1
            row = utils.convert_csv_row_empty_string_to_none(row)

            clearing_platform = create_clearing_platform(row, main_trend_coordinator_id, data_source)
            clearing_platform_success_records += 1
        except exceptions.ConstantNotFound as e:
            row['error'] = str(e)
            clearing_platform_errors.append(row)
        except exceptions.CreateClearingPlatformError as e:
            row['error'] = e.message
            clearing_platform_errors.append(row)
    pop_up_results.append(
        popup_utils.get_popup_record(ClearingPlatform, num_of_records, clearing_platform_success_records,
                                     clearing_platform_errors))
    return {constants.STR_MESSAGE: None, constants.STR_ERROR: False, 'popup_results': pop_up_results}
    response['inserted_records'] = PeriodicReception.create_ignore(periodic_receptions)
    response['additional_information'] = {'identity_error': identity_error, 'constant_errors': constant_errors}
    return response

class ClearingPlatformAPI(Resource):

    @staticmethod
    @login_required()
    def get(platform_id=None):
        if 'csv_template' in request.path:
            try:
                return File.Read.get_csv_template_by_name(CLEARING_PLATFORM_CSV_PARAMETER)
            except Exception as e:
                print(e)
                return {constants.STR_MESSAGE: messages.REQUEST_FILE_NOT_FOUND_ERROR, constants.STR_ERROR: True}
        if platform_id:
            results = ClearingPlatform.read(many=False, id=platform_id)
        else:
            results = ClearingPlatform.read()
        return jsonify(results)

    @staticmethod
    @login_required()
    def post():
        # Add from csv file
        if request.files and CLEARING_PLATFORM_CSV_PARAMETER in request.files:
            data_source = UPLOAD_SOURCES[0]
            csv_file = request.files[CLEARING_PLATFORM_CSV_PARAMETER]
            platform_parameters = request.form
            if not csv_file.filename:
                return {constants.STR_MESSAGE: messages.REQUEST_EMPTY_FILE_ERROR, constants.STR_ERROR: True}

            trend_coordinator_id = platform_parameters.get('trend_coordinator_id')
            clearing_platform_csv = File.Read.read_file(csv_file.read(), csv_file.filename)
            csv_reader = csv.DictReader(clearing_platform_csv)
            return create_clearing_platform_from_csv(csv_reader,trend_coordinator_id,data_source)
