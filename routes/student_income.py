import csv, re

from io import StringIO
from datetime import datetime
from core import messages, utils, date_utils
from flask import request
from flask_restful import Resource
from school_manager.constants import constants
from school_manager.constants.constants_lists import INCOME_PAYMENT_STATUS, EXPENSE_PAYMENT_STATUS, SCHOLARSHIP_TYPES
from school_manager.modules import exceptions
from school_manager.modules.file.file import File
from school_manager.modules.excellence_fund_allotment.excellence_fund_allotment import get_allotment_fund

from school_manager.models.student import Student
from school_manager.models.income import Income
from school_manager.models.bank_account import BankAccount
from school_manager.models.institution import Institution
from school_manager.models.course_enrollment import CourseEnrollment
from school_manager.models.trend_coordinator_attribution import TrendCoordinationAttribution
from school_manager.models.expense import Expense

from school_manager.constants.constants import UT8_WITH_BOM_ENCODING
from school_manager.routes.auth import login_required

from school_manager.modules import exceptions
from school_manager.modules import popup_utils

STUDENTS_INCOMES_CSV_PARAMETER = "students_incomes_csv"
CSV_ROWS_TO_SKIP = 2
CSV_SECOND_STATE_NEW_LINE = 2

IDENTITY_COL = "StudentIdentity"
IDENTITY_TYPE_COL = "IdentityType"
AMOUNT_COL = "ReasonLevelName"
PAYMENT_REASON_COL = "PaymentReasonName"
INSTITUTION_BRANCH_COL = "Textbox145"
COURSE_START_DATE = "DateFrom"
COURSE_END_DATE = "DateTo"
COURSE_TYPE = "StudyTypeNumber1"

def get_payment_month_from_csv(first_two_rows):
    parsed_date = date_utils.parse_date_from_str(first_two_rows[1].split(",")[0])
    parsed_date.replace(day=1)
    print(parsed_date)
    return parsed_date.isoformat()


def convert_string_to_datetime(date_string, date_format='%d/%m/%Y'):
    if not date_string: return None
    try:
        return datetime.strptime(date_string, date_format)
    except Exception as e:
        return None


def get_student_id(identity, identity_type):
    if not identity:
        raise exceptions.NoneValueException("student identity")
    student = Student.get_student_by_identity(identity, identity_type)
    if not student:
        raise exceptions.StudentNotExist(identity)
    return student.get('id')


def get_course_enrollment_id(student_id, branch_id, course_type, start_date, end_date):
    if start_date:
        start_date = start_date.isoformat()
    if end_date:
        end_date = end_date.isoformat()
    course_enrollments = CourseEnrollment.read(many=True, fk_student_id=student_id, fk_branch_id=branch_id,
                                               course_type=course_type)
    if not course_enrollments:
        course = CourseEnrollment.create(dict(course_type=course_type, fk_student_id=student_id, fk_branch_id=branch_id,
                                              start_date=start_date, end_date=start_date))
    else:
        course = CourseEnrollment.update({**course_enrollments[-1], **dict(start_date=start_date, end_date=end_date)},
                                         id=course_enrollments[-1].get('id'))
    return course[constants.STR_DATA].get('id')


def get_trend_coordinator_attribution(course_enrollment_id):
    if not course_enrollment_id: return None
    trend_attribution = TrendCoordinationAttribution.read(fk_course_enrollment_id=course_enrollment_id, many=False)
    return trend_attribution


def update_incomes(course_enrollment_id, end_date):
    if not course_enrollment_id: return None
    income = Income.read(many=False, fk_course_enrollment=course_enrollment_id)
    if not income: return

    income['payment_status'] = INCOME_PAYMENT_STATUS[4]
    income['fk_course_enrollment'] = None
    update_income = Income.update(income, id=income.get('id'))
    if update_income[constants.STR_ERROR]:
        raise exceptions.UpdateIncomeError(message=update_income[constants.STR_MESSAGE])


def update_expenses(course_enrollment_id, end_date):
    expenses = []
    if not course_enrollment_id: return None
    expense = Expense.read(many=False, fk_course_enrollment=course_enrollment_id)
    if not expense: return
    if expense['payment_status'] == EXPENSE_PAYMENT_STATUS[0]:
        delete_expense = Expense.delete(id=expense.get('id'))
        if delete_expense[constants.STR_ERROR]: raise exceptions.DeleteExpenseError(message=delete_expense[constants.STR_MESSAGE])
        return
    expense['scholarship_type'] = SCHOLARSHIP_TYPES[4]
    expense['fk_course_enrollment'] = None
    update_expense = Expense.update(expense, id=expense.get('id'))
    if update_expense[constants.STR_ERROR]:
        raise exceptions.UpdateExpenseError(message=update_expense[constants.STR_MESSAGE])
    # expenses.append(expense)


def get_institution_branch_from_csv_row(institution_branch_text, institutions_branches_map):
    regex = re.search(r"\s(\d+).*?\s(\d+)", institution_branch_text)
    institution_identity = regex.group(1)
    branch_symbol = int(regex.group(2))
    institution_id = institutions_branches_map.get(institution_identity, {}).get("id", None)
    if not institution_id:
        raise exceptions.InstitutionNotExist(institution_identity)
    branch_id = institutions_branches_map.get(institution_identity, {}).get("branches", {}). \
        get(branch_symbol, {}).get("id", None)
    if not branch_id:
        raise exceptions.BranchNotExist(institution_identity=institution_identity, symbol=branch_symbol)
    return institution_id, branch_id


def create_income(income_record):
    income = Income.create(income_record)
    if income[constants.STR_ERROR]:
        raise exceptions.CreateIncomeError(message=str(income[constants.STR_MESSAGE]))
    return income[constants.STR_DATA]

def update_allotment(row, income_record, trend_coordinator_attribution):
        income_amount, excellence_fund_allotment, eligibility_method, eligibility_min, eligibility_level = \
            get_allotment_fund(trend_coordinator_attribution, row.get(AMOUNT_COL))

        income_record['amount'] = income_amount
        income_record['excellence_fund_allotment'] = excellence_fund_allotment
        income_record['eligibility_method'] = eligibility_method
        income_record['eligibility_min'] = eligibility_min
        income_record['eligibility_level'] = eligibility_level

        return income_record

def validate_sixteen_month(fk_course_enrollment_id, course_end_date, payment_sixteen_month_date,update_previous):
    if course_end_date and course_end_date < payment_sixteen_month_date or update_previous:
        update_incomes(fk_course_enrollment_id, course_end_date)
        update_expenses(fk_course_enrollment_id, course_end_date)


def create_income_record(csv_row, for_month, fk_income_source_id, payment_method, payment_status, fk_bank_account_id,
                         institutions_branches_map,course_start_date, course_end_date):


    fk_institution_id, fk_branch_id = get_institution_branch_from_csv_row(csv_row.get(INSTITUTION_BRANCH_COL),
                                                                          institutions_branches_map)

    fk_student_id = get_student_id(csv_row.get(IDENTITY_COL), csv_row.get(IDENTITY_TYPE_COL))
    fk_course_enrollment_id = get_course_enrollment_id(fk_student_id, fk_branch_id, csv_row.get(COURSE_TYPE),
                                                       course_start_date, course_end_date)
    trend_coordinator_attribution = get_trend_coordinator_attribution(fk_course_enrollment_id)

    income_record = dict(for_month=for_month, amount=csv_row.get(AMOUNT_COL),
                         payment_reason=csv_row.get(PAYMENT_REASON_COL), fk_bank_account_id=fk_bank_account_id,
                         method=payment_method, payment_status=payment_status,
                         fk_institution_id=fk_institution_id, fk_student_id=fk_student_id,
                         fk_income_source_id=fk_income_source_id, fk_trend_coordinator_id=trend_coordinator_attribution.get('fk_trend_coordinator_id'),
                         fk_course_enrollment_id=fk_course_enrollment_id,
                         fk_branch_id=fk_branch_id,
                         excellence_fund_allotment=None,
                         eligibility_method=None,
                         eligibility_min=None, eligibility_level=None)

    return income_record, trend_coordinator_attribution


def create_income_from_csv(csv_reader, payment_month, fk_income_source_id, payment_method,
                           payment_status, fk_bank_account_id, update_previous=False):
    pop_up_results = []
    num_of_records, income_success_records = 0, 0
    income_errors = []
    payment_sixteen_month_date = datetime.strptime(payment_month, constants.ISO_FORMAT).replace(day=16)
    institutions_branches_map = Institution.get_institutions_branches_symbol_map()
    for row in csv_reader:
        num_of_records += 1
        try:
            row = utils.convert_csv_row_empty_string_to_none(row)
            course_start_date, course_end_date = convert_string_to_datetime(
                row.get(COURSE_START_DATE)), convert_string_to_datetime(row.get(COURSE_END_DATE))

            income_record, trend_coordinator_attribution = create_income_record(row, payment_month, fk_income_source_id, payment_method, payment_status, fk_bank_account_id,
                                                                                institutions_branches_map,course_start_date, course_end_date)
            validate_sixteen_month(income_record.get('fk_course_enrollment_id'), course_end_date,payment_sixteen_month_date,update_previous)
            income_record = update_allotment(row, income_record, trend_coordinator_attribution)
            income = create_income(income_record)

            income_success_records += 1
        except (exceptions.BranchNotExist, exceptions.InstitutionNotExist, exceptions.StudentNotExist,
                exceptions.ExcellenceAllotmentError) as e:
            row['error'] = e.message
            income_errors.append(row)
        except Exception as e:
            row['error'] = str(e)
            income_errors.append(row)
    pop_up_results.append(
        popup_utils.get_popup_record(Income, num_of_records, income_success_records, income_errors))
    return {constants.STR_MESSAGE: None, constants.STR_ERROR: False, 'popup_results': pop_up_results}


class StudentIncomeAPI(Resource):
    @staticmethod
    @login_required()
    def get():
        if 'csv_template' in request.path:
            try:
                return File.Read.get_csv_template_by_name(STUDENTS_INCOMES_CSV_PARAMETER)
            except Exception as e:
                print(e)
                return {constants.STR_MESSAGE: messages.REQUEST_FILE_NOT_FOUND_ERROR, constants.STR_ERROR: True}

    @staticmethod
    @login_required()
    def post():
        # Add from csv file
        if request.files and STUDENTS_INCOMES_CSV_PARAMETER in request.files:
            incomes_parameters = request.form
            required_params = ['fk_income_source_id', 'method', 'payment_status', 'account_number']
            if not all([required_param in incomes_parameters for required_param in required_params]):
                return {constants.STR_MESSAGE: messages.REQUEST_WRONG_FORM_PARAMETERS, constants.STR_ERROR: True}

            students_incomes_csv_file = request.files[STUDENTS_INCOMES_CSV_PARAMETER]
            if not students_incomes_csv_file.filename:
                return {constants.STR_MESSAGE: messages.REQUEST_EMPTY_FILE_ERROR, constants.STR_ERROR: True}

            account_number = incomes_parameters['account_number']
            fk_bank_account_id, fk_institution_id = BankAccount.get_bank_account_institution_id(account_number)
            if not fk_bank_account_id or not fk_institution_id:
                error_message = messages.REQUEST_WRONG_FORM_PARAMETERS_EXTENDED.format(
                    f'Could not find bank account or institution for account number {account_number}')
                return {constants.STR_MESSAGE: error_message, constants.STR_ERROR: True}
            students_incomes_csv = File.Read.read_file(students_incomes_csv_file.read(),
                                                       students_incomes_csv_file.filename, without_stringio=True)
            students_incomes_csv_data = students_incomes_csv.split(
                constants.NEW_LINE)
            # Skip the first two rows that contains not tabular data (PaymentMonth)
            students_incomes_csv = StringIO(
                constants.NEW_LINE.join(students_incomes_csv_data[CSV_ROWS_TO_SKIP:]))
            payment_month = get_payment_month_from_csv(
                students_incomes_csv_data[:CSV_ROWS_TO_SKIP])
            csv_reader = csv.DictReader(students_incomes_csv)

            return create_income_from_csv(csv_reader, payment_month,
                                          incomes_parameters['fk_income_source_id'], incomes_parameters['method'],
                                          incomes_parameters['payment_status'], fk_bank_account_id)

        return {constants.STR_MESSAGE: messages.REQUEST_EMPTY_FILE_ERROR, constants.STR_ERROR: True}
