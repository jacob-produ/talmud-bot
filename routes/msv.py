import csv, sys, re
from io import StringIO
from datetime import datetime
from core import messages, utils
from flask import request
from flask_restful import Resource
from school_manager.constants import constants
from school_manager.constants.constants_lists import EXPENSE_PAYMENT_STATUS, EXPENSE_PAYMENT_METHODS
from school_manager.modules.file.file import File

from school_manager.models.msv_file import MSVFile
from school_manager.models.bank_account import BankAccount
from school_manager.models.expense import Expense

from school_manager.models.student import Student
from school_manager.models.employee import Employee
from school_manager.models.supplier import Supplier

from school_manager.routes.auth import login_required

from school_manager.modules import exceptions
from school_manager.modules import popup_utils

from school_manager.constants.constants_lists import UPLOAD_SOURCES


MSV_CSV_PARAMETER = "msv_expense_csv"

ATTRIBUTION_IDENTITY_COL = "תעודת זהות"
AMOUNT_COL = "סכום לתשלום"
PAYMENT_METHOD = EXPENSE_PAYMENT_METHODS[1]
PAYMENT_STATUS = EXPENSE_PAYMENT_STATUS[3]
AMOUNT_REGEX = '\d+[,]*\d+[.]*\d+'
NEW_LINE = "\n"
CSV_ROWS_TO_SKIP = 2


def get_bank_account_institution_id(account_number):
    bank_account_record = BankAccount.read(['id', 'fk_institution_id'], many=False, account_number=account_number)
    return bank_account_record.get('id'), bank_account_record.get('fk_institution_id')


def create_msv_file(amount,**expense_params):
    # create msv_file
    msv_file = MSVFile.create(
        dict(amount=float(amount), date=expense_params.get('msv_sending_date').isoformat(), file_name=None),
        with_commit=True, many=False)

    if msv_file[constants.STR_ERROR]:
        raise exceptions.CreateMSVFileError(
            message=str(msv_file[constants.STR_MESSAGE]))
    return msv_file[constants.STR_DATA]


def create_expense(row, amount, msv_file_id, attribution_id, data_source,**expense_params):
    attribution, attribution_identity = expense_params.get('attribution'), row.get(ATTRIBUTION_IDENTITY_COL)
    expense_dict = dict(amount=float(amount),
                        payment_method=PAYMENT_METHOD, payment_status=PAYMENT_STATUS,
                        for_month=expense_params.get('for_month').isoformat(),
                        fk_bank_account_id=expense_params.get('fk_bank_account_id'),
                        fk_institution_id=expense_params.get('fk_institution_id'),
                        fk_msv_file_id=msv_file_id,
                        fk_trend_coordinator_id=expense_params.get('fk_trend_coordinator_id'),
                        data_source=data_source)
    attribution_dict = {f'fk_{attribution}_id': attribution_id}
    expense_dict = {**expense_dict, **attribution_dict}

    expense = Expense.create(expense_dict)
    if expense[constants.STR_ERROR]:
        raise exceptions.CreateExpenseError(
            message=str(expense[constants.STR_MESSAGE]))
    return expense[constants.STR_DATA]


def create_msv_expense_from_csv(csv_reader, **expense_params):
    pop_up_results = []
    num_of_records, msv_file_success_records, expense_success_records = 0, 0, 0
    expense_errors, msv_file_errors = [], []
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
            amount = re.search(AMOUNT_REGEX, row.get(AMOUNT_COL)).group(0).replace(',', '')
            print(amount)
            msv_file = create_msv_file( amount, **expense_params)
            msv_file_success_records += 1

            expense = create_expense(row, amount, msv_file.get('id'), attribution_id, data_source,**expense_params)
            expense_success_records += 1

        except exceptions.CreateMSVFileError as e:
            row['error'] = e.message
            msv_file_errors.append(row)
        except exceptions.CreateExpenseError as e:
            row['error'] = e.message
            expense_errors.append(row)
        except (exceptions.AttributionNotFoundError, Exception) as e:
            row['error'] = str(e)
            expense_errors.append(row)

        pop_up_results.append(
            popup_utils.get_popup_record(MSVFile, num_of_records, msv_file_success_records,
                                         msv_file_errors))
        pop_up_results.append(
            popup_utils.get_popup_record(Expense, num_of_records, expense_success_records,
                                         expense_errors))

        return {constants.STR_MESSAGE: None, constants.STR_ERROR: False, 'popup_results': pop_up_results}


class MSVExpenseAPI(Resource):
    @staticmethod
    @login_required()
    def get():
        if 'csv_template' in request.path:
            try:
                return File.Read.get_csv_template_by_name(MSV_CSV_PARAMETER)
            except Exception as e:
                print(e)
                return {constants.STR_MESSAGE: messages.REQUEST_FILE_NOT_FOUND_ERROR, constants.STR_ERROR: True}

    @staticmethod
    @login_required()
    def post():
        # Add from csv file
        if request.files and MSV_CSV_PARAMETER in request.files:
            data_source = UPLOAD_SOURCES[0]
            csv_file = request.files[MSV_CSV_PARAMETER]
            if not csv_file.filename:
                return {constants.STR_MESSAGE: messages.REQUEST_EMPTY_FILE_ERROR, constants.STR_ERROR: True}
            params = request.form
            if 'account_number' not in params or 'for_month' not in params or 'attribution' not in params:
                return {constants.STR_MESSAGE: messages.REQUEST_WRONG_FORM_PARAMETERS, constants.STR_ERROR: True}

            attribution, account_number, for_month = params['attribution'], int(
                params['account_number']), datetime.strptime(params['for_month'], '%d/%m/%Y')
            msv_sending_date = datetime.strptime(params['msv_sending_date'], '%d/%m/%Y')
            fk_trend_coordinator_id = params.get('fk_trend_coordinator_id')
            fk_bank_account_id, fk_institution_id = get_bank_account_institution_id(account_number)
            if not fk_bank_account_id or not fk_institution_id:
                error_message = messages.REQUEST_WRONG_FORM_PARAMETERS_EXTENDED.format(
                    f'Could not find bank account or institution for account number {account_number}')
                return {constants.STR_MESSAGE: error_message, constants.STR_ERROR: True}
            csv_data = File.Read.read_file(csv_file.read(), csv_file.filename, without_stringio=True)
            csv_data = csv_data.split(NEW_LINE)
            msv_csv = StringIO(NEW_LINE.join(csv_data[CSV_ROWS_TO_SKIP:]))
            csv_reader = csv.DictReader(msv_csv)
            return create_msv_expense_from_csv(csv_reader, attribution=attribution, account_number=account_number,
                                               for_month=for_month, fk_bank_account_id=fk_bank_account_id,
                                               fk_institution_id=fk_institution_id,
                                               fk_trend_coordinator_id=fk_trend_coordinator_id,
                                               msv_sending_date=msv_sending_date,
                                               data_source=data_source)

        else:
            return {constants.STR_MESSAGE: messages.REQUEST_EMPTY_FILE_ERROR, constants.STR_ERROR: True}
