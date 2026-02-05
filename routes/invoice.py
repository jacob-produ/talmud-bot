import os, re
from datetime import datetime

from core import messages
from school_manager.constants import constants
from flask import request
from flask_restful import Resource
from school_manager.routes.auth import login_required

from school_manager.models.institution import Institution
from school_manager.models.trend_coordinator import TrendCoordinator
from school_manager.models.supplier import Supplier
from school_manager.models.invoice import Invoice
from school_manager.models.expense import Expense

from school_manager.modules import exceptions
from school_manager.modules import popup_utils
from school_manager.modules.constants_validation import ConstantsValidation

from school_manager.constants.constants_lists import UPLOAD_SOURCES

# get school_manger path
DIR_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INVOICE_PATH = 'assets/invoice/'
DEFAULT_EXPORT_PATH = os.path.join(DIR_PATH, INVOICE_PATH)

INVOICE_FILE_PARAMETER = "invoice_file"
INVOICE_PARAMETERS = ['institution_identity', 'trend_coordinator_name',
                      'supplier_identity', 'invoice_date',
                      'amount', 'invoice_number']


def create_expense(institution_identity, trend_coordinator_name, supplier_identity, amount):
    institution_id = Institution.read(only_columns_list=['id'], many=False, identity=institution_identity).get('id')
    trend_coordinator_id = TrendCoordinator.get_trend_coordinator_by_name(name=trend_coordinator_name,
                                                                          many=False).get(
        'id')
    supplier_id = Supplier.read(only_columns_list=['id'], many=False, identity=supplier_identity).get('id')

    new_expense = dict(fk_supplier_id=supplier_id, amount=amount, fk_trend_coordinator_id=trend_coordinator_id,
                       fk_institution_id=institution_id)
    expense = Expense.create(new_expense)
    if expense[constants.STR_ERROR]:
        raise exceptions.CreateExpenseError(
            message=str(expense[constants.STR_MESSAGE]))
    return expense[constants.STR_DATA]


def create_invoice(expense_id, invoice_file, invoice_file_suffix, incomes_parameters,data_source):
    invoice_file_path = os.path.join(DEFAULT_EXPORT_PATH, f'{expense_id}.{invoice_file_suffix}')
    invoice_file.save(invoice_file_path)
    relative_invoice_path = os.path.join(INVOICE_PATH, f'{expense_id}.{invoice_file_suffix}')
    # create invoice
    new_invoice = dict(invoice_date=incomes_parameters['invoice_date'],
                       invoice_number=incomes_parameters['invoice_number'],
                       payment_due_date=incomes_parameters.get('payment_due_date'),
                       invoice_file_name=relative_invoice_path, fk_expense_id=expense_id,
                       data_source=data_source)
    invoice = Invoice.create(new_invoice)
    if invoice[constants.STR_ERROR]:
        raise exceptions.CreateExpenseError(
            message=str(invoice[constants.STR_MESSAGE]))
    return invoice[constants.STR_DATA]


def create_expense_invoice(institution_identity, trend_coordinator_name, supplier_identity, amount, invoice_file,
                           invoice_file_suffix, incomes_parameters,data_source):
    pop_up_results = []
    num_of_records, expense_success_records, invoice_success_records = 0, 0, 0
    expense_errors, invoice_errors = [], []
    try:
        expense = create_expense(institution_identity, trend_coordinator_name, supplier_identity, amount)
        expense_success_records += 1

        invoice = create_invoice(expense.get('id'), invoice_file,invoice_file_suffix,  incomes_parameters,data_source)
        invoice_success_records += 1

    except exceptions.CreateExpenseError as e:
        error_dict = dict(institution_identity=institution_identity, trend_coordinator_name=trend_coordinator_name,
                          supplier_identity=supplier_identity, amount=amount,
                          error=e.message)
        expense_errors.append(error_dict)
    except exceptions.CreateInvoiceError as e:
        error_dict = dict(invoice_date=incomes_parameters.get('invoice_date'),
                          trend_coordinator_name=incomes_parameters.get('trend_coordinator_name'),
                          supplier_identity=supplier_identity, amount=amount,
                          error=e.message)
        invoice_errors.append(error_dict)
    except Exception as e:
        error_dict = dict(institution_identity=institution_identity, trend_coordinator_name=trend_coordinator_name,
                          supplier_identity=supplier_identity, amount=amount,
                          error=str(e))
        expense_errors.append(error_dict)

    pop_up_results.append(
        popup_utils.get_popup_record(Expense, num_of_records, expense_success_records,
                                     expense_errors))
    pop_up_results.append(
        popup_utils.get_popup_record(Invoice, num_of_records, invoice_success_records,
                                     invoice_errors))

    return {constants.STR_MESSAGE: None, constants.STR_ERROR: False, 'popup_results': pop_up_results}


class InvoiceAPI(Resource):

    @login_required()
    def post(self):
        if request.files and INVOICE_FILE_PARAMETER in request.files:
            data_source = UPLOAD_SOURCES[0]
            incomes_parameters = request.form
            if not set(INVOICE_PARAMETERS).difference(incomes_parameters) == set():
                return {constants.STR_MESSAGE: messages.REQUEST_WRONG_FORM_PARAMETERS, constants.STR_ERROR: True}
            invoice_file = request.files[INVOICE_FILE_PARAMETER]
            invoice_file_suffix = invoice_file.filename.split(".")[-1]

            return create_expense_invoice(incomes_parameters['institution_identity'],
                                          incomes_parameters['trend_coordinator_name'],
                                          incomes_parameters['supplier_identity'], incomes_parameters['amount'],
                                          invoice_file, invoice_file_suffix, incomes_parameters,data_source)


        else:
            return {constants.STR_MESSAGE: messages.REQUEST_EMPTY_FILE_ERROR, constants.STR_ERROR: True}
