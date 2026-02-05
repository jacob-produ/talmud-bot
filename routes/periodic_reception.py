import csv
from core import messages, utils
from flask_restful import Resource
from school_manager.constants import constants
from dateutil.parser import parse as date_parser
from flask import request, jsonify
from school_manager.modules.file.file import File

from school_manager.modules.constants_validation import ConstantsValidation
from school_manager.modules import exceptions
from school_manager.modules import popup_utils

from school_manager.models.periodic_reception import PeriodicReception
from school_manager.models.student import Student
from school_manager.models.donator import Donator
from school_manager.models.trend_coordinator import TrendCoordinator
from school_manager.models.bank_account import BankAccount

from school_manager.routes.auth import login_required

from school_manager.constants.constants_lists import UPLOAD_SOURCES

PERIODIC_RECEPTION_CSV_PARAMETER = "periodic_reception_csv"

AMOUNT_COL = "סכום"
DONATOR_CREDIT_FOUR_DIGITS = "תורם"
STUDENT_IDENTITY_COL = "תז תלמיד"
TREND_COORDINATOR_NAME_COL = "שם מנחה"
CHARGES_AMOUNT_COL = "כמות חיובים"
PAYMENT_METHOD_COL = "שיטת תשלום"
PAYMENT_STATUS_COL = "סטטוס"
FIRST_CHARGE_DATE_COL = "תאריך חיוב ראשון"
LAST_CHARGE_DATE_COL = "תארי חיוב אחרון"
CHARGE_DATE_COL = "תאריך גבייה"

NEW_LINE = "\n"


COLS_DTYPES = {
    "סכוםץ": "float",
    "תז תלמיד": "int",
    "כמות חיובים": "int",
    "תאריך חיוב ראשון": "date",
    "תארי חיוב אחרון": "date",
    "תאריך גבייה": "int"
}

def get_bank_account_institution_id(account_number):
    bank_account_record = BankAccount.read(['id', 'fk_institution_id'], many=False, account_number=account_number)
    return bank_account_record.get('id'), bank_account_record.get('fk_institution_id')


def parse_date(date_string):
    try:
        date = date_parser(date_string)
    except Exception as e:
        date = None
    return date

def constants_validation(row):
    ConstantsValidation.periodic_reception_status_validation(row[PAYMENT_STATUS_COL])
    ConstantsValidation.periodic_reception_method_validation(row[PAYMENT_METHOD_COL])

def create_periodic_reception(row, fk_bank_account_id, fk_institution_id, data_source):
    donator_credit_four_digits = row[DONATOR_CREDIT_FOUR_DIGITS]
    student_id, trend_coordinator_id = None, None
    amount, charges_amount = row[AMOUNT_COL], row[CHARGES_AMOUNT_COL]
    payment_status, payment_method = row[PAYMENT_STATUS_COL], row[PAYMENT_METHOD_COL].replace('\"', '')
    first_charge_date, last_charge_date, charge_date = parse_date(row[FIRST_CHARGE_DATE_COL]), parse_date(
        row[LAST_CHARGE_DATE_COL]), row[CHARGE_DATE_COL]
    student_identity, trend_coordinator_name = row[STUDENT_IDENTITY_COL], row[TREND_COORDINATOR_NAME_COL]

    donator_id = Donator.read(many=False, credit_four_digits=donator_credit_four_digits).get('id')
    if not donator_id:
        donator = Donator.create(dict(credit_four_digits=donator_credit_four_digits))
        donator_id = donator[constants.STR_DATA].get('id')


    student_id = Student.read(many=False, identity=student_identity).get('id')
    trend_coordinator_id = TrendCoordinator.get_trend_coordinator_by_name(name=trend_coordinator_name,
                                                                              many=False).get('id')


    periodic_reception_dict = dict(amount=float(amount), first_charge_date=first_charge_date,
                                   last_charge_date=last_charge_date,
                                   charge_date=charge_date, periodic_reception_status=payment_status,
                                   fk_donator_id=donator_id,
                                   fk_institution_id=fk_institution_id,
                                   fk_trend_coordinator_id=trend_coordinator_id, fk_student_id=student_id,
                                   fk_bank_account_id=fk_bank_account_id, payment_method=payment_method,
                                   charges=charges_amount, data_source=data_source)

    periodic_reception = PeriodicReception.create(periodic_reception_dict)
    if periodic_reception[constants.STR_ERROR]:
        raise exceptions.CreatePeriodicReceptionError(
            message=str(periodic_reception[constants.STR_MESSAGE]))
    return periodic_reception[constants.STR_DATA]


def create_periodic_reception_from_csv(csv_reader, fk_bank_account_id, fk_institution_id, data_source):
    pop_up_results = []
    num_of_records, periodic_reception_success_records = 0, 0
    constants_errors, periodic_reception_errors = [], []
    for row in csv_reader:
        try:
            num_of_records += 1
            row = utils.convert_csv_row_empty_string_to_none(row)
            row = utils.convert_csv_row_dtype(row, COLS_DTYPES)

            periodic_reception = create_periodic_reception(row, fk_bank_account_id, fk_institution_id, data_source)
            periodic_reception_success_records += 1
        except exceptions.ConstantNotFound as e:
            row['error'] = str(e)
            periodic_reception_errors.append(row)
        except exceptions.CreatePeriodicReceptionError as e:
            row['error'] = e.message
            periodic_reception_errors.append(row)
    pop_up_results.append(
        popup_utils.get_popup_record(PeriodicReception, num_of_records, periodic_reception_success_records,
                                     periodic_reception_errors))
    return {constants.STR_MESSAGE: None, constants.STR_ERROR: False, 'popup_results': pop_up_results}
    response['inserted_records'] = PeriodicReception.create_ignore(periodic_receptions)
    response['additional_information'] = {'identity_error': identity_error, 'constant_errors': constant_errors}
    return response


class PeriodicReceptionAPI(Resource):

    @staticmethod
    @login_required()
    def get():
        if 'csv_template' in request.path:
            try:
                return File.Read.get_csv_template_by_name(PERIODIC_RECEPTION_CSV_PARAMETER)
            except Exception as e:
                print(e)
                return {constants.STR_MESSAGE: messages.REQUEST_FILE_NOT_FOUND_ERROR, constants.STR_ERROR: True}

    @staticmethod
    @login_required()
    def post():
        # Add from csv file
        if request.files and PERIODIC_RECEPTION_CSV_PARAMETER in request.files:
            data_source = UPLOAD_SOURCES[1]
            csv_file = request.files[PERIODIC_RECEPTION_CSV_PARAMETER]
            if not csv_file.filename:
                return {constants.STR_MESSAGE: messages.REQUEST_EMPTY_FILE_ERROR, constants.STR_ERROR: True}
            params = request.form
            if 'account_number' not in params:
                return {constants.STR_MESSAGE: messages.REQUEST_WRONG_FORM_PARAMETERS, constants.STR_ERROR: True}

            account_number = int(params['account_number'])
            fk_bank_account_id, fk_institution_id = get_bank_account_institution_id(account_number)
            if not fk_bank_account_id or not fk_institution_id:
                return {constants.STR_MESSAGE: messages.REQUEST_WRONG_FORM_PARAMETERS, constants.STR_ERROR: True}

            periodic_reception_data = File.Read.read_file(csv_file.read(), csv_file.filename)
            check_reader = csv.DictReader(periodic_reception_data)
            return create_periodic_reception_from_csv(check_reader,
                                                      fk_bank_account_id=fk_bank_account_id,
                                                      fk_institution_id=fk_institution_id,
                                                      data_source=data_source)

        else:
            periodic_reception_json = request.get_json()
            return jsonify(PeriodicReception.create(periodic_reception_json))

    @login_required()
    def put(self, periodic_reception_id):
        user_json = request.get_json()
        return jsonify(PeriodicReception.update(user_json, id=periodic_reception_id))
