import csv
from core import messages, utils
import pandas as pd
from school_manager.db import db
from flask import request
from flask_restful import Resource
from school_manager.constants import constants
from school_manager.constants.constants_lists import INCOME_PAYMENT_METHODS
from school_manager.models.income_source import IncomeSource, DEFAULT_CLEARING_ACCOUNT_IS
from school_manager.models.income import Income
from school_manager.models.bank_account import BankAccount
from school_manager.models.trend_coordinator import TrendCoordinator
from school_manager.models.student import Student
from school_manager.models.donator import Donator
from school_manager.models.clearing_credit import ClearingCredit
from school_manager.models.clearing_platform import ClearingPlatform

from school_manager.routes.auth import login_required
from datetime import datetime

from school_manager.modules.file.file import File
from school_manager.modules import exceptions
from school_manager.modules import popup_utils

from school_manager.constants.constants_lists import UPLOAD_SOURCES

CSV_SCHEMAS = {
    "Export": 0,
    "Trans": 1
}
CURRENT_CSV_SCHEMA = 0

CLEARING_CSV_PARAMETER = "clearing_payments_csv"

# MANDATORY_COLUMNS_TYPE_1 = [DONATOR_IDENTITY_TYPE_1,CLEARING_AMOUNT,CLEARING_CURRENCY,CLEARING_DATE_TYPE_1,DONATOR_FOUR_DIGITS,CLEARING_CREDIT_VALIDITY,
#                             CLEARING_COMPANY_TYPE_1,CLEARING_TRANSACTION_NUMBER,TREND_COORDINATOR_NAME]
# MANDATORY_COLUMNS_TYPE_2 = [CLEARING_TRANSACTION_NUMBER,CLEARING_DATE_TYPE_2,DONATOR_FOUR_DIGITS,CLEARING_AMOUNT,CLEARING_CONFIRMATION_NUMBER,
#                             CLEARING_CREDIT_BRAND,STUDENT_IDENTITY,TREND_COORDINATOR_NAME]

CLEARING_AMOUNT = "סכום"
CLEARING_CURRENCY = "מטבע"
CLEARING_DATE_TYPE_1 = "תאריך עסקה"
CLEARING_DATE_TYPE_2 = "תאריך"
CLEARING_DATE = (CLEARING_DATE_TYPE_1, CLEARING_DATE_TYPE_2)
CLEARING_COMPANY_TYPE_1 = "חברה סולקת"
CLEARING_COMPANY_TYPE_2 = "סולק"
CLEARING_COMPANY = (CLEARING_COMPANY_TYPE_1, CLEARING_COMPANY_TYPE_2)
CLEARING_DESCRIPTION_TYPE_1 = "עבור"
CLEARING_DESCRIPTION_TYPE_2 = "תיאור עסקה"
CLEARING_DESCRIPTION = (CLEARING_DESCRIPTION_TYPE_1, CLEARING_DESCRIPTION_TYPE_2)
CLEARING_COMMENTS = "הערות"
CLEARING_TRANSACTION_NUMBER = "מספר עסקה"
CLEARING_CONFIRMATION_NUMBER = "מספר אישור"
CLEARING_CREDIT_VALIDITY = "תוקף"
CLEARING_CREDIT_BRAND = "מותג"

DONATOR_IDENTITY_TYPE_1 = "מספר זהות"
DONATOR_IDENTITY_TYPE_2 = "ת.ז"
DONATOR_IDENTITY = (DONATOR_IDENTITY_TYPE_1, DONATOR_IDENTITY_TYPE_2)
DONATOR_FIRST_NAME_TYPE_1 = "שם"
DONATOR_FIRST_NAME_TYPE_2 = "שם פרטי"
DONATOR_FIRST_NAME = (DONATOR_FIRST_NAME_TYPE_1, DONATOR_FIRST_NAME_TYPE_2)
DONATOR_LAST_NAME_TYPE_1 = "שם"
DONATOR_LAST_NAME_TYPE_2 = "שם משפחה"
DONATOR_LAST_NAME = (DONATOR_LAST_NAME_TYPE_1, DONATOR_LAST_NAME_TYPE_2)
DONATOR_ADDRESS = "כתובת"
DONATOR_MAIL = "מייל"
DONATOR_FOUR_DIGITS = "4 ספרות אחרונות"

STUDENT_IDENTITY = "מזהה תלמיד"

TREND_COORDINATOR_NAME = "שם מנחה"

SUPPORTED_CURRENCIES = ("1", "שקל")
PAYMENT_METHOD = INCOME_PAYMENT_METHODS[4]

MANDATORY_COLUMNS_TYPE_1 = [DONATOR_IDENTITY_TYPE_1, CLEARING_AMOUNT, CLEARING_CURRENCY, CLEARING_DATE_TYPE_1,
                            DONATOR_FOUR_DIGITS, CLEARING_CREDIT_VALIDITY,
                            CLEARING_COMPANY_TYPE_1, CLEARING_TRANSACTION_NUMBER, TREND_COORDINATOR_NAME]
MANDATORY_COLUMNS_TYPE_2 = [CLEARING_TRANSACTION_NUMBER, CLEARING_DATE_TYPE_2, DONATOR_FOUR_DIGITS, CLEARING_AMOUNT,
                            CLEARING_CONFIRMATION_NUMBER,
                            CLEARING_CREDIT_BRAND, STUDENT_IDENTITY, TREND_COORDINATOR_NAME]

COLS_DTYPES = {
    CLEARING_AMOUNT: "float",
    CLEARING_CURRENCY: "int",
    CLEARING_DATE_TYPE_1: "date",
    CLEARING_DATE_TYPE_2: "date",
    CLEARING_COMPANY_TYPE_1: "string",
    CLEARING_COMPANY_TYPE_2: "string",
    CLEARING_DESCRIPTION_TYPE_1: "string",
    CLEARING_DESCRIPTION_TYPE_2: "string",
    CLEARING_COMMENTS: "string",
    CLEARING_TRANSACTION_NUMBER: "int",
    CLEARING_CONFIRMATION_NUMBER: "int",
    CLEARING_CREDIT_VALIDITY: "string",
    CLEARING_CREDIT_BRAND: "string",
    DONATOR_IDENTITY_TYPE_1: "int",
    DONATOR_IDENTITY_TYPE_2: "int",
    DONATOR_FIRST_NAME_TYPE_1: "string",
    DONATOR_FIRST_NAME_TYPE_2: "string",
    DONATOR_LAST_NAME_TYPE_1: "string",
    DONATOR_LAST_NAME_TYPE_2: "string",
    DONATOR_ADDRESS: "string",
    DONATOR_MAIL: "string",
    DONATOR_FOUR_DIGITS: "int",
    STUDENT_IDENTITY: "string",
    TREND_COORDINATOR_NAME: "string"
}


def validate_transaction_number(transaction_number_list, platform_id):
    query = db.session.query(ClearingCredit.fk_platform_id, ClearingCredit.clearing_transaction_number).filter_by(
        fk_platform_id=platform_id).order_by(
        ClearingCredit.clearing_transaction_number.desc())
    clearing_df = pd.read_sql(query.statement, db.engine)
    previous_platform_transactions = clearing_df['clearing_transaction_number'].tolist()
    return previous_platform_transactions, set(transaction_number_list).intersection(
        set(previous_platform_transactions))


def get_student_id(row):
    student_identity = row.get(STUDENT_IDENTITY, None)
    fk_student_id = Student.read(only_columns_list=['id'], many=False, identity=student_identity).get('id')
    if fk_student_id is None:
        raise exceptions.StudentNotExist(student_identity)
    return fk_student_id


def get_trend_coordinator_id(row, main_trend_coordinator_id):
    if main_trend_coordinator_id:
        return main_trend_coordinator_id
    trend_name = row[TREND_COORDINATOR_NAME]

    fk_trend_coordinator_id = TrendCoordinator.get_trend_coordinator_by_name(
        name=trend_name,
        many=False).get('id')
    if fk_trend_coordinator_id is None:
        raise exceptions.TrendCoordinatorNotFoundError(trend_name)
    return fk_trend_coordinator_id


def get_donator(row):
    credit_four_digits, identity = row.get(DONATOR_FOUR_DIGITS), row.get(DONATOR_IDENTITY)
    first_name, last_name = row.get(DONATOR_FIRST_NAME[CURRENT_CSV_SCHEMA]), row.get(
        DONATOR_LAST_NAME[CURRENT_CSV_SCHEMA])
    address, mail = row.get(DONATOR_ADDRESS), row.get(DONATOR_MAIL)
    donator = Donator.read(many=False, credit_four_digits=credit_four_digits)
    if donator.get('id'):
        return donator
    city, street, street_number = None, None, None
    if not CURRENT_CSV_SCHEMA:
        first_name = first_name.split()[0]
        last_name = " ".join(last_name.split()[1:-1]) if len(last_name.split()) > 1 else None
        address = address.split()
        if len(address) > 0: city = address[0]
        if len(address) > 1: street = address[1]
        if len(address) > 2: street_number = address[2]

    fields = dict(identity=identity, first_name=first_name, last_name=last_name, city=city
                  , street=street, street_number=street_number, mail=mail, credit_four_digits=credit_four_digits)
    donator = Donator.create(fields)[constants.STR_DATA]
    if donator[constants.STR_ERROR]:
        raise exceptions.CreateDonatorError(message=str(donator[constants.STR_MESSAGE]))
    return donator[constants.STR_DATA]


def validate_transaction_gap(last_transaction, transaction_number):
    if last_transaction and transaction_number - last_transaction != 1:
        message = messages.CLEARING_TRANSACTION_GAP.format(last_transaction, transaction_number)
        raise exceptions.ClearingTransactionGapError(message=message)


def validate_transaction_duplicate(transaction_number, duplicate_transactions):
    if transaction_number in duplicate_transactions:
        message = messages.CLEARING_TRANSACTION_DUPLICATE.format(transaction_number)
        raise exceptions.ClearingTransactionDuplicateError(message=message)


def create_income(row, transaction_date, fk_trend_coordinator_id, fk_student_id, fk_bank_account_id, fk_institution_id,
                  clearing_fk_income_source_id, fk_donator_id):
    income_record = dict(amount=row[CLEARING_AMOUNT], for_month=transaction_date,
                         deposit_date=transaction_date, method=PAYMENT_METHOD,
                         fk_bank_account_id=fk_bank_account_id, fk_institution_id=fk_institution_id,
                         fk_trend_coordinator_id=fk_trend_coordinator_id,
                         fk_income_source_id=clearing_fk_income_source_id, fk_donator_id=fk_donator_id,
                         fk_student_id=fk_student_id)
    income = Income.create(income_record)
    if income[constants.STR_ERROR]:
        raise exceptions.CreateIncomeError(message=str(income[constants.STR_MESSAGE]))
    return income[constants.STR_DATA]


def create_clearing(row, transaction_date, fk_platform_id, fk_income_id, data_source):
    clearing_credit_record = dict(original_amount=row[CLEARING_AMOUNT],
                                  source_coin=bool(row[CLEARING_CURRENCY]),
                                  credit_four_digits=row.get(DONATOR_FOUR_DIGITS),
                                  transaction_date=transaction_date,
                                  clearing_transaction_number=row.get(CLEARING_TRANSACTION_NUMBER),
                                  clearing_company=row.get(CLEARING_COMPANY[CURRENT_CSV_SCHEMA]),
                                  clearing_description=row.get(CLEARING_DESCRIPTION[CURRENT_CSV_SCHEMA]),
                                  clearing_comments=row.get(CLEARING_COMMENTS),
                                  confirmation_number=row.get(CLEARING_CONFIRMATION_NUMBER),
                                  credit_validity=row.get(CLEARING_CREDIT_VALIDITY),
                                  credit_brand=row.get(CLEARING_CREDIT_BRAND),
                                  fk_platform_id=fk_platform_id, fk_income_id=fk_income_id,
                                  data_source=data_source)

    clearing = ClearingCredit.create(clearing_credit_record)
    if clearing[constants.STR_ERROR]:
        raise exceptions.CreateClearingError(message=str(clearing[constants.STR_MESSAGE]))
    return clearing[constants.STR_DATA]


# def create_clearing_income_from_csv(csv_reader, fk_platform_id, fk_bank_account_id, fk_institution_id,
#                                     clearing_fk_income_source_id,
#                                     previous_platform_transaction,
#                                     duplicate_transaction,data_source,
#                                     main_trend_coordinator_id=None):
#     last_transaction = previous_platform_transaction[-1] if previous_platform_transaction else None
#     transaction_gap = False
#     clearing_credits = []
#     errors = []
#     response = {}
#     for row in csv_reader:
#         error_messages = []
#         transaction_number = row.get(CLEARING_TRANSACTION_NUMBER)
#         if transaction_gap:
#             continue
#         if not transaction_number:
#             error_messages.append(messages.CLEARING_NO_TRANSACTION_NUMBER)
#             errors.append((row, error_messages))
#             continue
#         if last_transaction and int(transaction_number) - int(last_transaction) != 1:
#             message = messages.CLEARING_TRANSACTION_GAP.format(last_transaction, transaction_number)
#             error_messages.append(message)
#             errors.append((row, error_messages))
#             transaction_gap = True
#             continue
#         if transaction_number in duplicate_transaction:
#             error_messages.append(messages.CLEARING_TRANSACTION_DUPLICATE)
#             errors.append((row, error_messages))
#             last_transaction = transaction_number
#             continue
#         last_transaction = transaction_number
#         if row.get(CLEARING_AMOUNT) and row.get(CLEARING_DATE[CURRENT_CSV_SCHEMA]) and row.get(
#                 CLEARING_TRANSACTION_NUMBER):
#
#             donator_id = validate_donator(row.get(DONATOR_FOUR_DIGITS), row.get(DONATOR_IDENTITY[CURRENT_CSV_SCHEMA]),
#                                           row.get(DONATOR_FIRST_NAME[CURRENT_CSV_SCHEMA]),
#                                           row.get(DONATOR_LAST_NAME[CURRENT_CSV_SCHEMA]),
#                                           row.get(DONATOR_ADDRESS), row.get(DONATOR_MAIL))
#             try:
#                 transaction_date = datetime.strptime(row[CLEARING_DATE[CURRENT_CSV_SCHEMA]], "%d/%m/%Y %H:%M")
#             except Exception as e:
#                 transaction_date = datetime.strptime(row[CLEARING_DATE[CURRENT_CSV_SCHEMA]], "%d/%m/%Y")
#             clearing_credit_record = dict(original_amount=float(row[CLEARING_AMOUNT]),
#                                           source_coin=bool(row[CLEARING_CURRENCY]),
#                                           credit_four_digits=row.get(DONATOR_FOUR_DIGITS),
#                                           transaction_date=transaction_date.isoformat(),
#                                           clearing_transaction_number=row.get(CLEARING_TRANSACTION_NUMBER),
#                                           clearing_company=row.get(CLEARING_COMPANY[CURRENT_CSV_SCHEMA]),
#                                           clearing_description=row.get(CLEARING_DESCRIPTION[CURRENT_CSV_SCHEMA]),
#                                           clearing_comments=row.get(CLEARING_COMMENTS),
#                                           confirmation_number=row.get(CLEARING_CONFIRMATION_NUMBER),
#                                           credit_validity=row.get(CLEARING_CREDIT_VALIDITY),
#                                           credit_brand=row.get(CLEARING_CREDIT_BRAND),
#                                           fk_platform_id=fk_platform_id)
#
#             income_record = dict(amount=float(row[CLEARING_AMOUNT]), for_month=transaction_date.isoformat(),
#                                  deposit_date=transaction_date.isoformat(), method=PAYMENT_METHOD,
#                                  fk_bank_account_id=fk_bank_account_id, fk_institution_id=fk_institution_id,
#                                  fk_trend_coordinator_id=None,
#                                  fk_income_source_id=clearing_fk_income_source_id, fk_donator_id=donator_id)
#             # student association
#             student_identity = row.get(STUDENT_IDENTITY, None)
#             if student_identity:
#                 attribution_id = Student.read(only_columns_list=['id'], many=False, identity=student_identity).get('id',
#                                                                                                                    None)
#                 if attribution_id:
#                     income_record['fk_student_id'] = attribution_id
#                 else:
#                     error_messages.append(messages.READ_FAIL.format("student"))
#             # trend association
#             if main_trend_coordinator_id:
#                 income_record['fk_trend_coordinator_id'] = main_trend_coordinator_id
#             elif row[TREND_COORDINATOR_NAME]:
#                 fk_trend_coordinator_id = TrendCoordinator.get_trend_coordinator_by_name(
#                     name=row[TREND_COORDINATOR_NAME],
#                     many=False).get('id')
#                 if fk_trend_coordinator_id:
#                     income_record['fk_trend_coordinator_id'] = fk_trend_coordinator_id
#                 else:
#                     error_messages.append(messages.READ_FAIL.format("trend_coordinator"))
#             if len(error_messages) > 0:
#                 errors.append((income_record, error_messages))
#
#             income_query = Income.create(income_record)
#             new_income = income_query[constants.STR_DATA]
#
#             clearing_credit_record['fk_income_id'] = new_income.get('id')
#             clearing_credits.append(clearing_credit_record)
#
#     response["inserted_records"] = ClearingCredit.create_ignore(clearing_credits, with_commit=True)
#     if len(errors) > 0:
#         response["uninserted_records"] = errors
#
#     return response


def create_clearing_from_csv(csv_reader, fk_platform_id, fk_bank_account_id, fk_institution_id,
                             clearing_fk_income_source_id,
                             previous_platform_transaction,
                             duplicate_transaction,data_source,
                             main_trend_coordinator_id=None):
    pop_up_results = []
    num_of_records = 0
    clearing_success_records, income_success_records, donator_success_records = 0, 0, 0
    clearing_errors, income_errors, donator_errors = [], [], []
    mandatory_columns = MANDATORY_COLUMNS_TYPE_1 if not CURRENT_CSV_SCHEMA else MANDATORY_COLUMNS_TYPE_2
    last_transaction = previous_platform_transaction[-1] if previous_platform_transaction else None
    for row in csv_reader:
        num_of_records += 1
        try:
            row = utils.convert_csv_row_empty_string_to_none(row)
            row = utils.convert_csv_row_dtype(row, COLS_DTYPES)
            popup_utils.validate_mandatory_columns(row, mandatory_columns)

            transaction_number, transaction_date = row[CLEARING_TRANSACTION_NUMBER], CLEARING_DATE[CURRENT_CSV_SCHEMA]
            validate_transaction_gap(last_transaction, transaction_number)
            validate_transaction_duplicate(transaction_number, duplicate_transaction)

            student_id, trend_id = get_student_id(row), get_trend_coordinator_id(row, main_trend_coordinator_id)
            donator = get_donator(row)

            income = create_income(row, transaction_date,trend_id, student_id, fk_bank_account_id, fk_institution_id,
                                   clearing_fk_income_source_id, donator.get('id'))
            clearing = create_clearing(row, transaction_date, fk_platform_id, income.get('id'), data_source)

            donator_success_records += 1
            income_success_records += 1
            clearing_success_records += 1

            last_transaction = transaction_number
        except (exceptions.StudentNotExist, exceptions.TrendCoordinatorNotFoundError,exceptions.CreateClearingError) as e:
            row['error'] = e.message
            clearing_errors.append(row)
        except exceptions.CreateDonatorError as e:
            row['error'] = e.message
            donator_errors.append(row)
        except exceptions.CreateIncomeError as e:
            row['error'] = e.message
            income_errors.append(row)
        except Exception as e:
            row['error'] = str(e)
            clearing_errors.append(row)
    pop_up_results.append(
        popup_utils.get_popup_record(ClearingCredit, num_of_records, clearing_success_records, clearing_errors))
    pop_up_results.append(
        popup_utils.get_popup_record(Income, num_of_records, income_success_records, income_errors))
    pop_up_results.append(
        popup_utils.get_popup_record(Donator, num_of_records, donator_success_records, donator_errors))

    return {constants.STR_MESSAGE: None, constants.STR_ERROR: False, 'popup_results': pop_up_results}


class ClearingAPI(Resource):

    @staticmethod
    @login_required()
    def get():
        if 'csv_template' in request.path:
            try:
                return File.Read.get_csv_template_by_name(CLEARING_CSV_PARAMETER)
            except Exception as e:
                print(e)
                return {constants.STR_MESSAGE: messages.REQUEST_FILE_NOT_FOUND_ERROR, constants.STR_ERROR: True}

    @staticmethod
    @login_required()
    def post():
        global CURRENT_CSV_SCHEMA
        # Add from csv file
        if request.files and CLEARING_CSV_PARAMETER in request.files:
            data_source = UPLOAD_SOURCES[0]
            clearing_payments_csv_file = request.files[CLEARING_CSV_PARAMETER]
            if not clearing_payments_csv_file.filename:
                return {constants.STR_MESSAGE: messages.REQUEST_EMPTY_FILE_ERROR, constants.STR_ERROR: True}

            incomes_parameters = request.form
            if 'fk_platform_id' not in incomes_parameters:
                return {constants.STR_MESSAGE: messages.REQUEST_WRONG_FORM_PARAMETERS, constants.STR_ERROR: True}
            platform_record = ClearingPlatform.read(many=False, id=incomes_parameters['fk_platform_id'])
            bank_account_record = BankAccount.read(many=False, id=platform_record.get('fk_bank_account_id'))

            fk_institution_id, fk_bank_account_id = bank_account_record.get(
                'fk_institution_id'), bank_account_record.get('id')
            fk_trend_coordinator_id = platform_record.get('fk_trend_coordinator_id')

            clearing_payments_csv_file = File.Read.read_file(clearing_payments_csv_file.read(),
                                                             clearing_payments_csv_file.filename)

            csv_reader = csv.DictReader(clearing_payments_csv_file)
            clearing_df = pd.DataFrame(csv_reader)
            clearing_df[CLEARING_TRANSACTION_NUMBER] = pd.to_numeric(clearing_df[CLEARING_TRANSACTION_NUMBER],
                                                                     errors='coerce')
            clearing_df = clearing_df.sort_values(CLEARING_TRANSACTION_NUMBER)
            previous_platform_transaction, duplicate_transaction = validate_transaction_number(
                clearing_df[CLEARING_TRANSACTION_NUMBER].tolist(), incomes_parameters['fk_platform_id'])

            fields_names = csv_reader.fieldnames
            csv_reader = clearing_df.to_dict("records")
            CURRENT_CSV_SCHEMA = CSV_SCHEMAS["Export"] if CLEARING_COMMENTS in fields_names else CSV_SCHEMAS["Trans"]
            clearing_fk_income_source_id = IncomeSource.read(name=DEFAULT_CLEARING_ACCOUNT_IS.get('name', ''),
                                                             many=False).get('id', None)
            return create_clearing_from_csv(csv_reader, fk_platform_id=incomes_parameters['fk_platform_id'],
                                                   fk_bank_account_id=fk_bank_account_id,
                                                   fk_institution_id=fk_institution_id,
                                                   clearing_fk_income_source_id=clearing_fk_income_source_id,
                                                   previous_platform_transaction=previous_platform_transaction,
                                                   duplicate_transaction=duplicate_transaction,
                                                   main_trend_coordinator_id=fk_trend_coordinator_id,
                                                   data_source=data_source)
