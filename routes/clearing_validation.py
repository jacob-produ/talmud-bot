import csv, re
from io import StringIO
from core import messages, utils
from flask import request
from flask_restful import Resource
from core.utils import convert_csv_row_empty_string_to_none, convert_csv_row_dtype
from school_manager.constants import constants
from school_manager.models.income import Income
from school_manager.models.trend_coordinator import TrendCoordinator
from school_manager.constants.constants import NEW_LINE
from school_manager.routes.auth import login_required

from school_manager.models.clearing_credit import ClearingCredit
from datetime import datetime
from school_manager.modules.file.file import File

from school_manager.modules import exceptions
from school_manager.modules import popup_utils

STRIP_REGEX = r"(\.\d)+"

HEADER_ROWS = 2

CLEARING_VALIDATION_CSV_PARAMETER = 'clearing_validation_csv'

AMOUNT = "סכום נטו"
CREDIT_NUMBER = "מספר כרטיס"
CONFIRMATION_NUMBER = "מספר אישור"
TRANSACTION_DATE = "תאריך קניה"

FEE_AMOUNT = "סכום עמלה"
VOUCHER_NUMBER = "מספר שובר"
CONVERSION_FACTOR = "מקדם המרה"
TERMINAL_NUMBER = "מספר מסוף"

VALUE_ADDED_TAX = 1.17

COLS_DTYPES = {
    "סכום נטו": "float",
    "מספר כרטיס": "string",
    "מספר אישור": "string",
    "סכום עמלה": "float",
    "מספר שובר": "string",
    "מקדם המרה": "float",
    "מספר מסוף": "string",
}


def parse_date(transaction_date):
    try:
        return datetime.strptime(transaction_date, '%d/%m/%Y')
    except Exception as e:
        return datetime(year=1950, month=1, day=1)


def get_platform_fee(trend_coordinator_id):
    if not trend_coordinator_id:
        return 0
    trend_coordinator = TrendCoordinator.read(many=False, id=trend_coordinator_id)
    return trend_coordinator.get('platform_fee', 0)


def update_clearing_transaction(row):
    original_amount, credit_number = float(row.get(AMOUNT)), row.get(CREDIT_NUMBER)
    confirmation_number, transaction_date = row.get(CONFIRMATION_NUMBER), parse_date(row.get(TRANSACTION_DATE))
    credit_four_digits = credit_number[-4:]

    fee_amount, voucher_number = float(row.get(FEE_AMOUNT)) * VALUE_ADDED_TAX, row.get(VOUCHER_NUMBER)
    conversion_factor, terminal_number = float(row.get(CONVERSION_FACTOR)), row.get(TERMINAL_NUMBER)

    clearing_query = ClearingCredit.read(many=False, transaction_date=transaction_date.isoformat(),
                                         original_amount=original_amount,
                                         credit_four_digits=credit_four_digits,
                                         confirmation_number=confirmation_number)
    if not clearing_query.get('id'):
        message = f"date={transaction_date.isoformat()}, amount={original_amount}, credit last 4 digits={credit_four_digits}," \
                  f" confirmation number={confirmation_number}"
        raise exceptions.ClearingTransactionNotFoundError(message)

    clearing_update = ClearingCredit.update(dict(fee_amount=fee_amount, voucher_number=voucher_number,
                                                 conversion_factor=conversion_factor,
                                                 terminal_number=terminal_number),
                                            id=clearing_query.get('id'))
    if clearing_update[constants.STR_ERROR]:
        raise exceptions.UpdateClearingError(
            message=str(clearing_update[constants.STR_MESSAGE]))
    return clearing_update[constants.STR_DATA]

def update_income(row, clearing_id):
    income_update = Income.update(dict(amount=row.get(AMOUNT)), id=clearing_id)

    if income_update[constants.STR_ERROR]:
        raise exceptions.UpdateIncomeError(
            message=str(income_update[constants.STR_MESSAGE]))
    return income_update[constants.STR_DATA]


def validate_clearing(csv_reader):
    pop_up_results = []
    num_of_records, clearing_success_records, income_success_records = 0, 0, 0
    income_failure_errors, clearing_failure_errors = [], []
    for row in csv_reader:

        try:
            num_of_records += 1
            row = utils.convert_csv_row_empty_string_to_none(row)

            clearing_transaction = update_clearing_transaction(row)
            clearing_success_records += 1

            income = update_income(row, clearing_transaction.get('id'))
            income_success_records += 1
        except exceptions.UpdateClearingError as e:
            row['error'] = e.message
            clearing_failure_errors.append(row)
        except exceptions.UpdateIncomeError as e:
            row['error'] = e.message
            income_failure_errors.append(row)
        except Exception as e:
            row['error'] = str(e)
            clearing_failure_errors.append(row)

    pop_up_results.append(
        popup_utils.get_popup_record(ClearingCredit, num_of_records, clearing_success_records,
                                     clearing_failure_errors))
    pop_up_results.append(
        popup_utils.get_popup_record(Income, num_of_records, income_success_records,
                                     income_failure_errors))

    return {constants.STR_MESSAGE: None, constants.STR_ERROR: False, 'popup_results': pop_up_results}


class ClearingValidationAPI(Resource):

    @staticmethod
    @login_required()
    def get():
        if 'csv_template' in request.path:
            try:
                return File.Read.get_csv_template_by_name(CLEARING_VALIDATION_CSV_PARAMETER)
            except Exception as e:
                print(e)
                return {constants.STR_MESSAGE: messages.REQUEST_FILE_NOT_FOUND_ERROR, constants.STR_ERROR: True}

    @staticmethod
    @login_required()
    def post():
        # Add from csv file
        if request.files and CLEARING_VALIDATION_CSV_PARAMETER in request.files:
            clearing_validation_csv_file = request.files[CLEARING_VALIDATION_CSV_PARAMETER]
            if not clearing_validation_csv_file.filename:
                return {constants.STR_MESSAGE: messages.REQUEST_EMPTY_FILE_ERROR, constants.STR_ERROR: True}

            clearing_validation_csv_file = File.Read.read_file(clearing_validation_csv_file.read(),
                                                               clearing_validation_csv_file.filename,
                                                               without_stringio=True)
            clearing_validation_csv_data = [row.strip() for row in clearing_validation_csv_file.split(NEW_LINE)]
            header = [row.split(',') for row in clearing_validation_csv_data[:HEADER_ROWS]]
            header = [[re.sub(STRIP_REGEX, '', word) for word in row] for row in header]
            header = ','.join(
                [re.sub(' +', ' ', f'{header[0][idx]} {header[1][idx]}'.strip()) for idx in range(len(header[0]))])
            data = NEW_LINE.join(clearing_validation_csv_data[HEADER_ROWS:])

            clearing_payments_csv = StringIO(f'{header}{NEW_LINE}{data}')
            csv_reader = csv.DictReader(clearing_payments_csv)
            return validate_clearing(csv_reader)
