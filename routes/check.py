import csv, sys, re

from core import messages, utils
from flask import request
from flask_restful import Resource
from school_manager.constants import constants
from school_manager.constants.constants_lists import EXPENSE_PAYMENT_METHODS
from dateutil.parser import parse as date_parser
from school_manager.models.trend_coordinator import TrendCoordinator
from school_manager.models.bank_account import BankAccount
from school_manager.models.expense import Expense
from school_manager.modules.file.file import File

from school_manager.models.student import Student
from school_manager.models.employee import Employee
from school_manager.models.supplier import Supplier

from school_manager.routes.auth import login_required

from school_manager.modules import exceptions
from school_manager.modules import popup_utils
from school_manager.modules.constants_validation import ConstantsValidation

from school_manager.constants.constants_lists import UPLOAD_SOURCES


CHECK_CSV_PARAMETER = "check_expense_csv"

ATTRIBUTION_IDENTITY_COL = "תז"
AMOUNT_COL = ["סכום", "שיקים.סכום"]
TREND_COORDINATOR_NAME = "הערות"
FOR_MONTH_COL = "עלחודש"
CHECK_DATE_COL = "תאריך"
CHECK_PRINTING_DATE_COL = "הודפס"
CHECK_NUMBER_COL = "מסשיק"
ACTUAL_PAYMENT_DATE_COL = "תאריךיציאה"
PAYMENT_STATUS_COL = "מצבשיק"
COMMENTS_COL = ["תתקטגוריה", "קודקטגוריה"]
PAYMENT_METHOD = EXPENSE_PAYMENT_METHODS[0]

RELEVANT_PAYMENT_STATUS = ['הודפס', 'נפרע', 'חודש', 'חזר']
AMOUNT_REGEX = '\d+[,]*\d+[.]*\d+'
NEW_LINE = "\n"
CSV_ROWS_TO_SKIP = 2


def get_bank_account_institution_id(account_number):
    bank_account_record = BankAccount.read(['id', 'fk_institution_id'], many=False, account_number=account_number)
    return bank_account_record.get('id'), bank_account_record.get('fk_institution_id')


def parse_date(date_string):
    try:
        date = date_parser(date_string)
    except Exception as e:
        date = None
    return date


def create_check_msv(row, attribution_id, current_state, data_source,**expense_params):
    attribution, attribution_identity = expense_params.get('attribution'), row.get(ATTRIBUTION_IDENTITY_COL)
    amount = re.search(AMOUNT_REGEX, row.get(AMOUNT_COL)).group(0).replace(',', '')
    expense_dict = dict(amount=float(amount), comments=row[COMMENTS_COL[current_state]],
                        payment_method=PAYMENT_METHOD, payment_status=row[PAYMENT_STATUS_COL],
                        for_month=parse_date(row[FOR_MONTH_COL]),
                        transmission_date=parse_date(row[CHECK_DATE_COL]),
                        check_printing_date=parse_date(row[CHECK_PRINTING_DATE_COL]),
                        check_number=int(row[CHECK_NUMBER_COL]),
                        actual_payment_date=parse_date(row[ACTUAL_PAYMENT_DATE_COL]),
                        fk_bank_account_id=expense_params.get('fk_bank_account_id'),
                        fk_institution_id=expense_params.get('fk_institution_id'),
                        data_source=data_source)
    attribution_dict = {f'fk_{attribution}_id': attribution_id}
    expense_dict = {**expense_dict, **attribution_dict}

    expense = Expense.create(expense_dict)
    if expense[constants.STR_ERROR]:
        raise exceptions.CreateExpenseError(
            message=str(expense[constants.STR_MESSAGE]))
    return expense[constants.STR_DATA]


def constants_validation(row):
    ConstantsValidation.expense_payment_status_validation(row.get(PAYMENT_STATUS_COL))


def create_check_expense_from_csv(csv_reader, **expense_params):
    pop_up_results = []
    num_of_records, expense_success_records = 0, 0
    expense_errors = []
    current_state = 0 if AMOUNT_COL[0] in csv_reader.fieldnames else 1
    for row in csv_reader:
        try:
            num_of_records += 1
            row = utils.convert_csv_row_empty_string_to_none(row)
            data_source = expense_params.get('data_source')
            attribution, attribution_identity = expense_params.get('attribution'), row.get(ATTRIBUTION_IDENTITY_COL)
            attribution_id = getattr(sys.modules[__name__], attribution.capitalize()) \
                .read(only_columns_list=['id'], many=False, identity=attribution_identity).get('id')
            if not attribution_id:
                raise exceptions.AttributionNotFoundError(attribution, attribution_identity)

            fk_trend_coordinator_id = TrendCoordinator.get_trend_coordinator_by_name(name=row[TREND_COORDINATOR_NAME],
                                                                                     many=False).get('id')
            if not fk_trend_coordinator_id:
                raise exceptions.TrendCoordinatorNotFoundError(row[TREND_COORDINATOR_NAME])

            expense = create_check_msv(row, attribution_id, current_state, data_source,**expense_params)
            expense_success_records += 1
        except exceptions.CreateExpenseError as e:
            row['error'] = e.message
            expense_errors.append(row)
        except (exceptions.AttributionNotFoundError, exceptions.TrendCoordinatorNotFoundError,
                exceptions.ExpensePaymentStatusConstantNotFound, Exception) as e:
            row['error'] = str(e)
            expense_errors.append(row)

        pop_up_results.append(
            popup_utils.get_popup_record(Expense, num_of_records, expense_success_records,
                                         expense_errors))

        return {constants.STR_MESSAGE: None, constants.STR_ERROR: False, 'popup_results': pop_up_results}


class CheckExpenseAPI(Resource):

    @staticmethod
    @login_required()
    def get():
        if 'csv_template' in request.path:
            try:
                return File.Read.get_csv_template_by_name(CHECK_CSV_PARAMETER)
            except Exception as e:
                print(e)
                return {constants.STR_MESSAGE: messages.REQUEST_FILE_NOT_FOUND_ERROR, constants.STR_ERROR: True}

    @staticmethod
    @login_required()
    def post():
        # Add from csv file
        if request.files and CHECK_CSV_PARAMETER in request.files:
            data_source = UPLOAD_SOURCES[0]
            csv_file = request.files[CHECK_CSV_PARAMETER]
            if not csv_file.filename:
                return {constants.STR_MESSAGE: messages.REQUEST_EMPTY_FILE_ERROR, constants.STR_ERROR: True}
            params = request.form
            if 'account_number' not in params or 'attribution' not in params:
                return {constants.STR_MESSAGE: messages.REQUEST_WRONG_FORM_PARAMETERS, constants.STR_ERROR: True}

            attribution, account_number = params['attribution'], int(params['account_number'])
            fk_bank_account_id, fk_institution_id = get_bank_account_institution_id(account_number)
            if not fk_bank_account_id or not fk_institution_id:
                return {constants.STR_MESSAGE: messages.REQUEST_WRONG_FORM_PARAMETERS, constants.STR_ERROR: True}
            check_data = File.Read.read_file(csv_file.read(), csv_file.filename)
            check_reader = csv.DictReader(check_data)
            return create_check_expense_from_csv(check_reader, attribution=attribution, account_number=account_number,
                                                 fk_bank_account_id=fk_bank_account_id,
                                                 fk_institution_id=fk_institution_id,
                                                 data_source=data_source)

        else:
            return {constants.STR_MESSAGE: messages.REQUEST_EMPTY_FILE_ERROR, constants.STR_ERROR: True}
