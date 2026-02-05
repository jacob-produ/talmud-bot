import csv
from core import messages, utils
from flask import request
from flask_restful import Resource
from school_manager.constants import constants

from school_manager.modules.file.file import File
from school_manager.modules.exceptions import ConstantNotFound

from school_manager.models.bank_account import BankAccount
from school_manager.models.expense import Expense

from school_manager.models.student import Student
from school_manager.models.course_enrollment import CourseEnrollment

from school_manager.routes.auth import login_required

from school_manager.modules import exceptions
from school_manager.modules import popup_utils
from school_manager.modules.constants_validation import ConstantsValidation

from school_manager.constants.constants_lists import UPLOAD_SOURCES


STUDENT_INSURANCE_CSV_PARAMETER = "student_insurance_expense_csv"

ATTRIBUTION_IDENTITY_COL = "תז"
AMOUNT_COL = "פרמיהחודשית"
FOR_MONTH_COL = "חודשנוכחי"
COURSE_TYPE_COL = "סוגלימוד"

COLS_DTYPES = {
    "תז": "string",
    "פרמיהחודשית": "float",
    "חודשנוכחי": "date",
    "סוגלימוד": "int",
}


def get_bank_account_institution_id(account_number):
    bank_account_record = BankAccount.read(['id', 'fk_institution_id'], many=False, account_number=account_number)
    return bank_account_record.get('id'), bank_account_record.get('fk_institution_id')


def get_student_course_enrollment(identity, course_type):
    student = Student.read(many=False, identity=identity)
    if not student:
        return None, None
    course = CourseEnrollment.read(many=False,fk_student_id=student.get('id'),
                                              course_type=course_type)
    if course:
        return student.get('id'), course.get('id')
    return None, None

def create_student_expense(row,**expense_params):
    attribution_identity = row.get(ATTRIBUTION_IDENTITY_COL)
    amount = row.get(AMOUNT_COL) + 1
    course_type = row[COURSE_TYPE_COL]
    student_id, course_enrollment_id = get_student_course_enrollment(attribution_identity, course_type)
    for_month = row.get(FOR_MONTH_COL)
    if not student_id:
        raise exceptions.StudentNotExist(attribution_identity)
    # create expense
    expense_dict = dict(amount=float(amount), fk_student_id=student_id, fk_course_enrollment_id=course_enrollment_id,
                        for_month=for_month.isoformat(),data_source=expense_params.get('data_source'),
                        fk_bank_account_id=expense_params.get('fk_bank_account_id'),
                        fk_institution_id=expense_params.get('fk_institution_id'))

    expense = Expense.create(expense_dict)
    if expense[constants.STR_ERROR]:
        raise exceptions.CreateExpenseError(
            message=str(expense[constants.STR_MESSAGE]))
    return expense[constants.STR_DATA]

def constants_validation(row):
    ConstantsValidation.course_type_validation(row[COURSE_TYPE_COL])


def create_student_expense_from_csv(csv_reader, **expense_params):
    pop_up_results = []
    num_of_records, expense_success_records = 0, 0
    expense_errors = []
    for row in csv_reader:
        try:
            num_of_records += 1
            row = utils.convert_csv_row_empty_string_to_none(row)
            # row = utils.convert_csv_row_dtype(row, COLS_DTYPES)
            constants_validation(row)

            expense = create_student_expense(row, **expense_params)
            expense_success_records += 1
        except exceptions.CreateExpenseError as e:
            row["חודשנוכחי"] = str(row["חודשנוכחי"])
            row['error'] = e.message
            expense_errors.append(row)
        except (exceptions.ConstantNotFound, exceptions.StudentNotExist, Exception) as e:
            row["חודשנוכחי"] = str(row["חודשנוכחי"])
            row['error'] = str(e)
            expense_errors.append(row)

    pop_up_results.append(
        popup_utils.get_popup_record(Expense, num_of_records, expense_success_records,
                                     expense_errors))

    return {constants.STR_MESSAGE: None, constants.STR_ERROR: False, 'popup_results': pop_up_results}




class StudentInsuranceAPI(Resource):
    @staticmethod
    @login_required()
    def get():
        if 'csv_template' in request.path:
            try:
                return File.Read.get_csv_template_by_name(STUDENT_INSURANCE_CSV_PARAMETER)
            except Exception as e:
                print(e)
                return {constants.STR_MESSAGE: messages.REQUEST_FILE_NOT_FOUND_ERROR, constants.STR_ERROR: True}

    @staticmethod
    @login_required()
    def post():
        # Add from csv file
        if request.files and STUDENT_INSURANCE_CSV_PARAMETER in request.files:
            data_source = UPLOAD_SOURCES[0]
            csv_file = request.files[STUDENT_INSURANCE_CSV_PARAMETER]
            if not csv_file.filename:
                return {constants.STR_MESSAGE: messages.REQUEST_EMPTY_FILE_ERROR, constants.STR_ERROR: True}
            params = request.form
            if 'account_number' not in params:
                return {constants.STR_MESSAGE: messages.REQUEST_WRONG_FORM_PARAMETERS, constants.STR_ERROR: True}

            account_number = params['account_number']
            fk_bank_account_id, fk_institution_id = get_bank_account_institution_id(account_number)
            if not fk_bank_account_id or not fk_institution_id:
                return {constants.STR_MESSAGE: messages.REQUEST_WRONG_FORM_PARAMETERS, constants.STR_ERROR: True}

            csv_data = File.Read.read_file(csv_file.read(), csv_file.filename)
            csv_reader = csv.DictReader(csv_data)
            return create_student_expense_from_csv(csv_reader, fk_bank_account_id=fk_bank_account_id,
                                                   fk_institution_id=fk_institution_id,data_source=data_source)

        else:
            return {constants.STR_MESSAGE: messages.REQUEST_EMPTY_FILE_ERROR, constants.STR_ERROR: True}
