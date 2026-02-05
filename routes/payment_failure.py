import csv

from core import messages, utils
from school_manager.constants import constants
from flask import request
from flask_restful import Resource
from school_manager.routes.auth import login_required
from school_manager.models.course_enrollment import CourseEnrollment
from school_manager.models.student import Student
from school_manager.models.payment_failure_code import PaymentFailureCode
from school_manager.models.payment_failure import PaymentFailure
from school_manager.models.income import Income

from school_manager.modules.file.file import File

from school_manager.modules import exceptions
from school_manager.modules import popup_utils

from school_manager.constants.constants_lists import UPLOAD_SOURCES

PAYMENT_FAILURE_CSV_PARAMETER = "payment_failure_csv"

STUDENT_IDENTITY = "StudentIdentity"
FAILURE_CODE = "ReasonID"
COURSE_TYPE = "StudyTypeNumber1"


def get_payment_failure_code(code):
    pf_code = PaymentFailureCode.read(many=False, code=code)
    if pf_code.get('id'):
        return pf_code.get('id')
    pf_code = PaymentFailureCode.create(dict(code=code))[constants.STR_DATA]
    return pf_code.get('id')


def get_student_course_enrollment(identity, course_type):
    student = Student.query.filter_by(identity=identity).first()
    if not student:
        return None, None
    course = CourseEnrollment.query.filter_by(fk_student_id=student.id,
                                              course_type=course_type).first()
    if course:
        return student.id, course.id
    return None, None


def create_payment_failure(row, data_source):
    attribution = 'student'
    student_id, course_enrollment_id = get_student_course_enrollment(row.get(STUDENT_IDENTITY), row.get(COURSE_TYPE))
    if not student_id:
        raise exceptions.StudentNotExist(row.get(STUDENT_IDENTITY))
    if not course_enrollment_id:
        raise exceptions.CourseEnrollmentNotExist()

    incomes = Income.read(many=True, amount=0, fk_student_id=student_id,
                          fk_course_enrollment_id=course_enrollment_id)
    if not incomes:
        message = f"amount={0}, student_identity={row.get(STUDENT_IDENTITY)}, course_type={row.get(COURSE_TYPE)}"
        raise exceptions.IncomeNotFoundError(message)
    income_id = incomes[-1].get('id')

    payment_failure_code_id = get_payment_failure_code(row.get(FAILURE_CODE))
    if not payment_failure_code_id:
        raise exceptions.PaymentFailureNotFoundError(code=row.get(FAILURE_CODE))
    payment_failure_record = dict(fk_payment_failure_id=payment_failure_code_id,
                                  fk_course_enrollment_id=course_enrollment_id,
                                  fk_income_id=income_id, data_source=data_source)

    payment_failure = PaymentFailure.create(payment_failure_record)
    if payment_failure[constants.STR_ERROR]:
        raise exceptions.CreatePaymentFailureError(
            message=str(payment_failure[constants.STR_MESSAGE]))
    return payment_failure[constants.STR_DATA]


def create_payment_failure_from_csv(csv_reader, data_source):
    pop_up_results = []
    num_of_records, payment_failure_success_records = 0, 0
    constants_errors, payment_failure_errors = [], []
    for row in csv_reader:

        try:
            num_of_records += 1
            row = utils.convert_csv_row_empty_string_to_none(row)

            payment_failure = create_payment_failure(row,data_source)
            payment_failure_success_records += 1
        except exceptions.CreatePaymentFailureError as e:
            row['error'] = e.message
            payment_failure_errors.append(row)
        except (exceptions.StudentNotExist, exceptions.CourseEnrollmentNotExist, exceptions.IncomeNotFoundError,
                exceptions.PaymentFailureNotFoundError, Exception) as e:
            row['error'] = str(e)
            payment_failure_errors.append(row)

    pop_up_results.append(
        popup_utils.get_popup_record(PaymentFailure, num_of_records, payment_failure_success_records,
                                     payment_failure_errors))

    return {constants.STR_MESSAGE: None, constants.STR_ERROR: False, 'popup_results': pop_up_results}


class PaymentFailureAPI(Resource):

    @staticmethod
    @login_required()
    def get():
        if 'csv_template' in request.path:
            try:
                return File.Read.get_csv_template_by_name(PAYMENT_FAILURE_CSV_PARAMETER)
            except Exception as e:
                print(e)
                return {constants.STR_MESSAGE: messages.REQUEST_FILE_NOT_FOUND_ERROR, constants.STR_ERROR: True}

    @staticmethod
    @login_required()
    def post():
        if request.files and PAYMENT_FAILURE_CSV_PARAMETER in request.files:
            data_source = UPLOAD_SOURCES[0]
            clearing_payments_csv_file = request.files[PAYMENT_FAILURE_CSV_PARAMETER]
            if not clearing_payments_csv_file.filename:
                return {constants.STR_MESSAGE: messages.REQUEST_EMPTY_FILE_ERROR, constants.STR_ERROR: True}

            clearing_payments_csv_file = File.Read.read_file(clearing_payments_csv_file.read(),
                                                             clearing_payments_csv_file.filename)
            csv_reader = csv.DictReader(clearing_payments_csv_file)
            return create_payment_failure_from_csv(csv_reader, data_source)
