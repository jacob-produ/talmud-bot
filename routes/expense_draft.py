import csv, sys, re
from io import StringIO
from datetime import datetime
from core import messages, utils
from flask import request
from flask_restful import Resource
from school_manager.constants import constants
from school_manager.constants.constants_lists import EXPENSE_PAYMENT_STATUS, EXPENSE_PAYMENT_METHODS
from school_manager.modules.file.file import File
from school_manager.constants.constants_lists import SCHOLARSHIP_TYPES

from school_manager.models.msv_file import MSVFile
from school_manager.models.bank_account import BankAccount
from school_manager.models.expense import Expense
from school_manager.models.invoice import Invoice

from school_manager.models.student import Student
from school_manager.models.employee import Employee
from school_manager.models.supplier import Supplier

from school_manager.constants.constants import UT8_WITH_BOM_ENCODING
from school_manager.routes.auth import login_required

from school_manager.modules import exceptions
from school_manager.modules import popup_utils
from school_manager.modules.constants_validation import ConstantsValidation

from school_manager.constants.constants_lists import UPLOAD_SOURCES

DRAFT_CSV_PARAMETER = "expense_draft_csv"

ATTRIBUTION_IDENTITY_COL = "תעודת זהות"
AMOUNT_COL = "סכום"
PAYMENT_STATUS = EXPENSE_PAYMENT_STATUS[0]
INVOICE_DATE = "תאריך חשבונית"
INVOICE_NUMBER = "מספר חשבונית"
NEW_LINE = "\n"

COLS_DTYPES = {
    ATTRIBUTION_IDENTITY_COL: "int",
    AMOUNT_COL: "float",
    INVOICE_DATE: "date",
    INVOICE_NUMBER: "int"
}

MANDATORY_COLUMNS = [ATTRIBUTION_IDENTITY_COL, AMOUNT_COL, INVOICE_DATE, INVOICE_NUMBER]


def get_bank_account_institution_id(account_number):
    bank_account_record = BankAccount.read(['id', 'fk_institution_id'], many=False, account_number=account_number)
    return bank_account_record.get('id'), bank_account_record.get('fk_institution_id')


def get_student_fixed_amount(student_id, for_month, amount):
    student_expenses = Expense.read(many=True, fk_student_id=student_id, scholarship_type=SCHOLARSHIP_TYPES[1])
    for_month_year, for_month_month = for_month.year, for_month.month
    for_month_format = '%Y-%m-%dT%H:%M:%S'
    for expense in student_expenses:
        if expense.get('for_month') and datetime.strptime(expense.get('for_month'),
                                                          for_month_format).year == for_month_year and datetime.strptime(
            expense.get('for_month'), for_month_format).month == for_month_month:
            return amount - expense.get('amount', 0)

    return amount

def get_student_id(student_identity):
    fk_student_id = Student.read(only_columns_list=['id'], many=False, identity=student_identity).get('id')
    if fk_student_id is None:
        raise exceptions.StudentNotExist(student_identity)
    return fk_student_id

def get_employee_id(employee_identity):
    fk_employee_id = Employee.read(only_columns_list=['id'], many=False, identity=employee_identity).get('id')
    if fk_employee_id is None:
        raise exceptions.EmployeeNotExist(employee_identity)
    return fk_employee_id

def get_supplier_id(supplier_identity):
    fk_supplier_id = Supplier.read(only_columns_list=['id'], many=False, identity=supplier_identity).get('id')
    if fk_supplier_id is None:
        raise exceptions.SupplierNotExist(supplier_identity)
    return fk_supplier_id

def get_attribution_id(attribution, attribution_identity):
    if attribution == 'student':
        return get_student_id(attribution_identity)
    elif attribution == 'employee':
        return get_employee_id(attribution_identity)
    elif attribution == 'supplier':
        return get_supplier_id(attribution_identity)
    else:
        raise exceptions.AttributionNotExist(attribution)

def get_amount(amount, fixed, for_month, attribution,scholarship_type, attribution_id):
    if fixed and attribution == 'student' and scholarship_type == SCHOLARSHIP_TYPES[2]:
        amount = get_student_fixed_amount(attribution_id, for_month, amount)
    return amount

def create_expense(amount, attribution, attribution_id, payment_method,for_month,fk_bank_account_id,
                   fk_institution_id,fk_trend_coordinator_id,scholarship_type, data_source):
    attribution_key = f'fk_{attribution}_id'
    attribution_dict = {attribution_key: attribution_id}
    expense_record = dict(amount=amount,
                        payment_method=payment_method,
                        for_month=for_month.isoformat(),
                        fk_bank_account_id=fk_bank_account_id,
                        fk_institution_id=fk_institution_id,
                        fk_trend_coordinator_id=fk_trend_coordinator_id,
                        scholarship_type=scholarship_type,
                          data_source=data_source)
    expense_record = {**attribution_dict, **expense_record}
    expense = Expense.create(expense_record)
    if expense[constants.STR_ERROR]:
        raise exceptions.CreateExpenseError(message=str(expense[constants.STR_MESSAGE]))
    return expense[constants.STR_DATA]

def create_invoice(row, fk_expense_id):
    invoice_record = dict(invoice_date=row[INVOICE_DATE], invoice_number=row[INVOICE_NUMBER],
                        fk_expense_id=fk_expense_id)

    invoice = Invoice.create(invoice_record)
    if invoice[constants.STR_ERROR]:
        raise exceptions.CreateInvoiceError(message=str(invoice[constants.STR_MESSAGE]))
    return invoice[constants.STR_DATA]

# def create_draft_expense_from_csv(csv_reader, **expense_params):
#     attribution_class = None
#     expenses = []
#     identity_error, expense_insertion_errors, invoice_insertion_errors = [], [], []
#     response = {}
#     for row in csv_reader:
#         if all([len(a) == 0 for a in row.values()]): continue
#         data_source = expense_params.get('data_source')
#         attribution, attribution_identity = expense_params.get('attribution'), row.get(ATTRIBUTION_IDENTITY_COL)
#         fixed, scholarship_type = expense_params.get('fixed'), expense_params.get('scholarship_type')
#         attribution_key = f'fk_{attribution}_id'
#
#         attribution_class = getattr(sys.modules[__name__], attribution.capitalize())
#         attribution_id = attribution_class.read(only_columns_list=['id'], many=False,
#                                                 identity=attribution_identity).get('id')
#         if not attribution_id:
#             identity_error.append(messages.READ_FAIL.format(f"identity={attribution_identity}"))
#
#         for_month = expense_params.get('for_month')
#         amount = float(row.get(AMOUNT_COL))
#         if fixed and attribution == 'student' and scholarship_type == SCHOLARSHIP_TYPES[2]:
#             amount = get_student_fixed_amount(attribution_id, for_month, amount)
#
#         # create expense
#         attribution_dict = {attribution_key: attribution_id}
#         expense_dict = dict(amount=float(amount),
#                             payment_method=expense_params.get('payment_method'), payment_status=PAYMENT_STATUS,
#                             for_month=for_month.isoformat(),
#                             fk_bank_account_id=expense_params.get('fk_bank_account_id'),
#                             fk_institution_id=expense_params.get('fk_institution_id'),
#                             fk_trend_coordinator_id=expense_params.get('fk_trend_coordinator_id'),
#                             scholarship_type=scholarship_type)
#         expense_dict = {**expense_dict, **attribution_dict}
#         if attribution_class != Supplier:
#             expenses.append(expense_dict)
#         else:
#             new_expense = Expense.create(expense_dict, with_commit=True, many=False)
#             invoice_number, invoice_date = row.get(INVOICE_NUMBER), row.get(INVOICE_DATE)
#             if new_expense[constants.STR_ERROR]:
#                 expense_insertion_errors.append(new_expense[constants.STR_MESSAGE])
#                 continue
#             new_expense_id = new_expense[constants.STR_DATA].get('id')
#             if invoice_date and invoice_number:
#                 invoice_date = datetime.strptime(invoice_date, '%d/%m/%Y').isoformat()
#                 invoice_dict = dict(invoice_date=invoice_date, invoice_number=invoice_number,
#                                     fk_expense_id=new_expense_id)
#                 new_invoice = Invoice.create(invoice_dict, with_commit=True, many=False)
#                 if new_invoice[constants.STR_ERROR]:
#                     invoice_insertion_errors.append(new_invoice[constants.STR_MESSAGE])
#     if attribution_class != Supplier:
#         response['inserted_records'] = Expense.create_ignore(expenses)
#     else:
#         response['inserted_records'] = {constants.STR_MESSAGE: messages.CREATE_SUCCESS.format(Expense.__name__),
#                                         constants.STR_DATA: None, constants.STR_ERROR: False}
#     response['additional_information'] = {'identity_errors': identity_error,
#                                           'expense_insertion_errors': expense_insertion_errors,
#                                           'invoice_insertion_errors': invoice_insertion_errors}
#     return response


def create_expense_from_csv(csv_reader, attribution, account_number,
                             for_month, fk_bank_account_id,fk_institution_id,
                             fk_trend_coordinator_id,fixed,payment_method,
                             scholarship_type,data_source):
    pop_up_results = []
    num_of_records = 0
    expense_success_records, invoice_success_records = 0, 0
    expense_errors, invoice_errors = [], []
    for row in csv_reader:
        num_of_records += 1
        try:
            row = utils.convert_csv_row_empty_string_to_none(row)
            row = utils.convert_csv_row_dtype(row, COLS_DTYPES)
            popup_utils.validate_mandatory_columns(row, MANDATORY_COLUMNS)

            attribution_id = get_attribution_id(attribution, row.get(ATTRIBUTION_IDENTITY_COL))
            amount = get_amount(row[AMOUNT_COL], fixed, for_month, attribution,scholarship_type, attribution_id)

            expense = create_expense(amount, attribution, attribution_id, payment_method,for_month,fk_bank_account_id,
                   fk_institution_id,fk_trend_coordinator_id,scholarship_type, data_source)

            if attribution == 'supplier':
                create_invoice(row, expense.get('id'))
                invoice_success_records += 1
            expense_success_records += 1
        except (exceptions.StudentNotExist, exceptions.EmployeeNotExist, exceptions.SupplierNotExist,
                exceptions.CreateExpenseError) as e:
            row['error'] = e.message
            expense_errors.append(row)
        except exceptions.CreateInvoiceError as e:
            row['error'] = e.message
            invoice_errors.append(row)
        except Exception as e:
            row['error'] = str(e)
            expense_errors.append(row)
    pop_up_results.append(
        popup_utils.get_popup_record(Expense, num_of_records, expense_success_records, expense_errors))
    pop_up_results.append(
        popup_utils.get_popup_record(Invoice, num_of_records, invoice_success_records, invoice_errors))
    return {constants.STR_MESSAGE: None, constants.STR_ERROR: False, 'popup_results': pop_up_results}


class ExpenseDraftAPI(Resource):

    @staticmethod
    @login_required()
    def get():
        if 'csv_template' in request.path:
            try:
                return File.Read.get_csv_template_by_name(DRAFT_CSV_PARAMETER)
            except Exception as e:
                print(e)
                return {constants.STR_MESSAGE: messages.REQUEST_FILE_NOT_FOUND_ERROR, constants.STR_ERROR: True}

    @staticmethod
    @login_required()
    def post():
        # Add from csv file
        if request.files and DRAFT_CSV_PARAMETER in request.files:
            data_source = UPLOAD_SOURCES[0]
            csv_file = request.files[DRAFT_CSV_PARAMETER]
            if not csv_file.filename:
                return {constants.STR_MESSAGE: messages.REQUEST_EMPTY_FILE_ERROR, constants.STR_ERROR: True}
            params = request.form
            required_params = ['account_number', 'for_month', 'attribution', 'fixed']
            if not all([required_param in params for required_param in required_params]):
                return {constants.STR_MESSAGE: messages.REQUEST_WRONG_FORM_PARAMETERS, constants.STR_ERROR: True}

            attribution, account_number, for_month = params['attribution'].lower(), int(
                params['account_number']), datetime.strptime(params['for_month'], '%d/%m/%Y')
            payment_method = params.get('payment_method')
            fk_trend_coordinator_id = params.get('fk_trend_coordinator_id')
            fk_bank_account_id, fk_institution_id = get_bank_account_institution_id(account_number)

            # if payment_method not in EXPENSE_PAYMENT_METHODS:
            #     error_message = messages.REQUEST_WRONG_FORM_PARAMETERS_EXTENDED.format(
            #         f'There is no payment method named: {payment_method}')
            #     return {constants.STR_MESSAGE: error_message, constants.STR_ERROR: True}
            if not fk_bank_account_id or not fk_institution_id:
                error_message = messages.REQUEST_WRONG_FORM_PARAMETERS_EXTENDED.format(
                    f'Could not find bank account or institution for account number {account_number}')
                return {constants.STR_MESSAGE: error_message, constants.STR_ERROR: True}

            csv_data = File.Read.read_file(csv_file.read(), csv_file.filename)
            csv_reader = csv.DictReader(csv_data)
            return create_draft_expense_from_csv(csv_reader, attribution=attribution, account_number=account_number,
                                                 for_month=for_month, fk_bank_account_id=fk_bank_account_id,
                                                 fk_institution_id=fk_institution_id,
                                                 fk_trend_coordinator_id=fk_trend_coordinator_id,
                                                 fixed=False if params.get('fixed') == 'false' else True,
                                                 payment_method=payment_method,
                                                 scholarship_type=params.get('scholarship_type'),
                                                 data_source=data_source)

        else:
            return {constants.STR_MESSAGE: messages.REQUEST_EMPTY_FILE_ERROR, constants.STR_ERROR: True}
