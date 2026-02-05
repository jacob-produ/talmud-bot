from core import messages, utils
from school_manager.constants import constants
from school_manager.modules import exceptions

from school_manager.models.institution import Institution
from school_manager.models.course_enrollment import CourseEnrollment
from school_manager.models.student import Student


from flask import request
from flask_restful import Resource
from school_manager.routes.auth import login_required
from io import StringIO

from school_manager.modules.file.file import File
from school_manager.modules.constants_validation import ConstantsValidation
from school_manager.modules import popup_utils

import csv
from datetime import datetime

COURSE_ENROLLMENT_CSV_PARAMETER = "course_enrollment_csv"
INSTITUTION_ROW = 1
INSTITUTION_COLUMN = 1
DATA_START_ROW = 3

BRANCH_SYMBOL = "Textbox237"
COURSE_TYPE = "StudyTypeID"
COURSE_ENROLLMENT_START_DATE = "DateFrom"
COURSE_ENROLLMENT_END_DATE = "DateTo"

STUDENT_IDENTITY = "StudentIdentity"
STUDENT_IDENTITY_TYPE = "IdentificationTypeName"
STUDENT_FIRST_NAME = "StudentName2"
STUDENT_LAST_NAME = "StudentFamilyName1"
STUDENT_COUNTRY = "CountryName"
STUDENT_MARTIAL_STATUS = "MarritalStatusName"
STUDENT_BIRTH_DATE = "BirthDate"


def get_institution_branches(institution_csv_rows):
    institution_identity = institution_csv_rows[INSTITUTION_ROW].split(',')[INSTITUTION_COLUMN]
    institution_branches_map = Institution.get_institutions_branches_symbol_map()

    if institution_identity not in institution_branches_map:
        raise exceptions.InstitutionNotExist(institution_identity)
    return institution_identity, institution_branches_map[institution_identity]['branches']


def get_student(csv_row):
    identity, identity_type = csv_row.get(STUDENT_IDENTITY), csv_row.get(STUDENT_IDENTITY_TYPE)
    first_name, last_name = csv_row.get(STUDENT_FIRST_NAME), csv_row.get(STUDENT_LAST_NAME)
    birth_date, martial_status = convert_string_to_datetime(csv_row.get(STUDENT_BIRTH_DATE)), csv_row.get(
        STUDENT_MARTIAL_STATUS)

    student = Student.get_student_by_identity(identity, identity_type)
    if not student:
        student_object = dict(identity=identity, identity_type=identity_type, first_name=first_name,
                              last_name=last_name,
                              birth_date=birth_date, marital_status=martial_status)
        student = Student.create(student_object)
        student = student[constants.STR_DATA]
    return student


def convert_string_to_datetime(date_string, date_format='%d/%m/%Y'):
    if not date_string: return None
    try:
        return datetime.strptime(date_string, date_format).isoformat()
    except Exception as e:
        return None


def convert_string_to_int(string):
    try:
        return int(string)
    except ValueError as e:
        return None

def constants_validation(row):
    ConstantsValidation.course_type_validation(row.get(COURSE_TYPE))
    ConstantsValidation.student_identity_type_validation(row.get(STUDENT_IDENTITY_TYPE))


def create_course_enrollment(row,institution_branches_map, institution_identity):
    branch_symbol = convert_string_to_int(row.get(BRANCH_SYMBOL))
    if branch_symbol not in institution_branches_map:
        raise exceptions.BranchNotExist(institution_identity, branch_symbol)
    branch_id = institution_branches_map[branch_symbol].get('id')

    student_id = get_student(row).get('id')
    if not student_id:
        raise exceptions.StudentNotExist(row.get(STUDENT_IDENTITY))
    course_start_date, course_end_date = convert_string_to_datetime(
        row.get(COURSE_ENROLLMENT_START_DATE)), convert_string_to_datetime(row.get(COURSE_ENROLLMENT_END_DATE))
    course_enrollment_record = dict(course_type=row.get(COURSE_TYPE),
                                    start_date=course_start_date, end_date=course_end_date,
                                    fk_student_id=student_id,
                                    fk_branch_id=branch_id)
    course_enrollment = CourseEnrollment.create(course_enrollment_record)
    if course_enrollment[constants.STR_ERROR]:
        raise exceptions.CreateCourseEnrollmentError(
            message=str(course_enrollment[constants.STR_MESSAGE]))
    return course_enrollment[constants.STR_DATA]

# TODO: return unfound
# TODO: return unique name error
# TODO: update if unique constraint happen
def create_course_enrollment_csv(csv_reader, institution_branches_map, institution_identity):
    pop_up_results = []
    num_of_records, course_enrollment_success_records = 0, 0
    constants_errors, course_enrollment_errors = [], []
    for row in csv_reader:
        try:
            num_of_records += 1
            row = utils.convert_csv_row_empty_string_to_none(row)
            constants_validation(row)
            course_enrollment = create_course_enrollment(row, institution_branches_map, institution_identity)
            course_enrollment_errors += 1

        except exceptions.StudentNotExist as e:
            row['error'] = str(e)
            course_enrollment_errors.append(row)
        except exceptions.BranchNotExist as e:
            row['error'] = str(e)
            course_enrollment_errors.append(row)
        except exceptions.ConstantNotFound as e:
            row['error'] = str(e)
            course_enrollment_errors.append(row)
        except exceptions.CreateCourseEnrollmentError as e:
            row['error'] = e.message
            course_enrollment_errors.append(row)
    pop_up_results.append(
        popup_utils.get_popup_record(CourseEnrollment, num_of_records, course_enrollment_success_records,
                                     course_enrollment_errors))


    return {constants.STR_MESSAGE: None, constants.STR_ERROR: False, 'popup_results': pop_up_results}
    enrollments = CourseEnrollment.create_ignore(course_enrollments)
    if not enrollments[constants.STR_ERROR]:
        num_of_inserted_enrollments = len(course_enrollments)
    else:
        num_of_inserted_enrollments = len(course_enrollments) - len(enrollments[constants.STR_DATA])
    inserted_enrollments = CourseEnrollment.get_last_enrollments(num_of_inserted_enrollments)
    response['inserted_records'] = enrollments
    response['additional_information'] = {
        'students_errors': student_errors,
        'branches_errors': branch_errors,
        'constant_errors': constant_errors,
        'attribution_errors' : []
    }
    return response, inserted_enrollments


class CourseEnrollmentAPI(Resource):

    @login_required()
    def get(self):
        if 'csv_template' in request.path:
            try:
                return File.Read.get_csv_template_by_name(COURSE_ENROLLMENT_CSV_PARAMETER)
            except Exception as e:
                print(e)
                return {constants.STR_MESSAGE: messages.REQUEST_FILE_NOT_FOUND_ERROR, constants.STR_ERROR: True}

    @login_required()
    def post(self):
        if request.files and COURSE_ENROLLMENT_CSV_PARAMETER in request.files:
            course_enrollment_csv_file = request.files[COURSE_ENROLLMENT_CSV_PARAMETER]
            if not course_enrollment_csv_file.filename:
                return {constants.STR_MESSAGE: messages.REQUEST_EMPTY_FILE_ERROR, constants.STR_ERROR: True}

            course_enrollment_csv = File.Read.read_file(course_enrollment_csv_file.read(),
                                                        course_enrollment_csv_file.filename, without_stringio=True)
            course_enrollment_data = course_enrollment_csv.split(constants.NEW_LINE)
            try:
                institution_identity, institution_branches_map = get_institution_branches(
                    course_enrollment_data[:INSTITUTION_ROW + 1])
            except exceptions.InstitutionNotExist as e:
                return {constants.STR_MESSAGE: str(e), constants.STR_ERROR: True}

            course_enrollment_csv_data = StringIO(constants.NEW_LINE.join(course_enrollment_data[DATA_START_ROW:]))
            csv_reader = csv.DictReader(course_enrollment_csv_data)
            return create_course_enrollment_csv(csv_reader, institution_branches_map,
                                                                          institution_identity)
            #TODO: return error
            try:
                CourseEnrollment.attribute_course_enrollment_to_trend_coordinator(inserted_enrollments)
            except Exception as e:
                response['attribution_errors'] = [dict(error=str(e),data=inserted_enrollments)]
            return response
