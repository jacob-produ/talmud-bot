from core import messages, utils
from school_manager.constants import constants
from school_manager.constants.course_types import COURSE_TYPE_MAP, MULTIPLE_DAY_PART_COURSES
from school_manager.models.course_enrollment import CourseEnrollment
from school_manager.models.student import Student
from school_manager.models.trend_coordinator import TrendCoordinator
from school_manager.models.trend_coordinator_attribution import TrendCoordinationAttribution
from school_manager.models.branch import Branch
from flask import request, jsonify
from flask_restful import Resource
from school_manager.routes.auth import login_required

from school_manager.modules.file.file import File
from school_manager.modules.constants_validation import ConstantsValidation
from school_manager.modules import exceptions
from school_manager.modules import popup_utils

from school_manager.constants.constants_lists import UPLOAD_SOURCES

import csv
from datetime import datetime

COURSE_ENROLLMENT_CSV_PARAMETER = "course_enrollment_trend_coordinator_attribution_csv"

COURSE_TYPE = "מסלול"
PROFESSION = "התמחות"
FUND_RAISER = "מגייס"
EXCELLENCE_SCHOLARSHIP = "מילגת מצוינות"
BASE_SCHOLARSHIP = "מילגת בסיס"
DEFAULT_SCHOLARSHIP = "מלגת ברירת מחדל"
TEACHING_SCHOLARSHIP = "מלגת לימוד"
TREND_ATTRIBUTION_START_DATE = "תאריך התחלה שיוך מנחה"
TREND_ATTRIBUTION_END_DATE = "תאריך סיום שיוך מנחה"
COURSE_ENROLLMENT_START_DATE = "תאריך התחלה רישום קורס"
COURSE_ENROLLMENT_END_DATE = "תאריך סיום שיוך מנחה רישום קורס"
PAYMENT_METHOD = "שיטת תשלום"
ELIGIBILITY_MIN = "זכאות מינימאלית"
ELIGIBILITY_METHOD = "שיטת זכאות"
ELIGIBILITY_LEVEL = "רמת זכאות"
ENROLLMENT_STATUS = "סטטוס רישום"
STUDENT_IDENTITY = "תעודת זהות"
STUDENT_IDENTITY_TYPE = "סוג זיהוי"
STUDENT_FIRST_NAME = "שם פרטי"
STUDENT_LAST_NAME = "שם משפחה"
BRANCH_SYMBOL = "סניף"
INSTITUTION_IDENTITY = "מספר מוסד"
TREND_COORDINATOR_NAME = "אחראי קבוצה"
AFTERNOON_TREND_COORDINATOR_NAME = "אחראי קבוצת צהריים"
DAY_PART = "חלק ביום"


def get_student(student_identity, student_identity_type, student_first_name, student_last_name):
    student = Student.read(many=False, identity=student_identity, identity_type=student_identity_type)
    if student:
        return student
    create_results = Student.create(
        dict(identity=student_identity, first_name=student_first_name, last_name=student_last_name
             , identity_type=student_identity_type))
    return create_results[constants.STR_DATA]


def convert_string_to_datetime(date_string, date_format='%d/%m/%Y'):
    if not date_string: return None
    try:
        return datetime.strptime(date_string, date_format).isoformat()
    except Exception as e:
        return None


def convert_string_to_int(string):
    try:
        return int(string)
    except Exception as e:
        return None


def get_trend_coordinator_payment_method(trend_coordinator_name):
    trend_coordinator = TrendCoordinator.read(many=False, name=trend_coordinator_name)
    return trend_coordinator.get('default_payment_method')


def create_course_enrollment(row, student_id, branch_id, data_source):
    student_enrollments = CourseEnrollment.read(many=True, fk_student_id=student_id)
    for enrollment in student_enrollments:
        if enrollment.get('fk_branch_id') == branch_id and enrollment.get('course_type') == int(row.get(COURSE_TYPE)):
            return enrollment

    course_start_date, course_end_date = convert_string_to_datetime(
        row.get(COURSE_ENROLLMENT_START_DATE)), convert_string_to_datetime(row.get(COURSE_ENROLLMENT_END_DATE))
    course_enrollment_record = dict(course_type=row.get(COURSE_TYPE), profession=row.get(PROFESSION),
                                    start_date=course_start_date, end_date=course_end_date,
                                    fk_student_id=student_id,
                                    enrollment_status=convert_string_to_int(row.get(ENROLLMENT_STATUS)),
                                    fk_branch_id=branch_id, data_source=data_source)
    course_enrollment = CourseEnrollment.create(course_enrollment_record)
    if course_enrollment[constants.STR_ERROR]:
        raise exceptions.CreateCourseEnrollmentError(
            message=str(course_enrollment[constants.STR_MESSAGE]))
    return course_enrollment[constants.STR_DATA]


def create_trend_attribution(row, student_id, course_enrollment_id, trend_coordinator_name, data_source):
    trend_coordinator_id = TrendCoordinator.get_trend_coordinator_by_name(trend_coordinator_name, many=False).get(
        'id')
    trend_start_date, trend_end_date = convert_string_to_datetime(
        row.get(COURSE_ENROLLMENT_START_DATE)), convert_string_to_datetime(row.get(COURSE_ENROLLMENT_END_DATE))
    trend_payment_method = row.get(PAYMENT_METHOD) if row.get(
        PAYMENT_METHOD) else get_trend_coordinator_payment_method(trend_coordinator_name)
    day_part = COURSE_TYPE_MAP.get(int(row.get(COURSE_TYPE)))
    trend_attribution_record = dict(fund_raiser=row.get(FUND_RAISER),
                                    excellence_scholarship=row.get(EXCELLENCE_SCHOLARSHIP),
                                    base_scholarship=row.get(BASE_SCHOLARSHIP),
                                    teaching_scholarship=row.get(TEACHING_SCHOLARSHIP),
                                    default_scholarship=row.get(DEFAULT_SCHOLARSHIP), start_date=trend_start_date,
                                    end_date=trend_end_date,
                                    payment_method=trend_payment_method,
                                    eligibility_min=convert_string_to_int(row.get(ELIGIBILITY_MIN)),
                                    eligibility_method=row.get(ELIGIBILITY_METHOD),
                                    eligibility_level=convert_string_to_int(row.get(ELIGIBILITY_LEVEL)),
                                    day_part=day_part,
                                    fk_student_id=student_id, fk_trend_coordinator_id=trend_coordinator_id,
                                    fk_course_enrollment_id=course_enrollment_id,
                                    data_source=data_source)

    trend_coordinator_attribution = TrendCoordinationAttribution.create(trend_attribution_record)
    if trend_coordinator_attribution[constants.STR_ERROR]:
        raise exceptions.CreateTrendCoordinatorAttributionError(
            message=str(trend_coordinator_attribution[constants.STR_MESSAGE]))
    return trend_coordinator_attribution[constants.STR_DATA]


def constants_validation(row):
    ConstantsValidation.student_identity_type_validation(row.get(STUDENT_IDENTITY_TYPE))
    ConstantsValidation.income_payment_method_validation(row.get(PAYMENT_METHOD))
    ConstantsValidation.course_type_validation(row.get(COURSE_TYPE))
    # ConstantsValidation.day_part_validation(row.get(DAY_PART))
    ConstantsValidation.eligibility_method_validation(row.get(ELIGIBILITY_METHOD))



def create_course_enrollment_trend_attribution_from_csv(csv_reader, data_source):
    pop_up_results = []
    num_of_records, course_enrollment_success_records, trend_attribution_success_records = 0, 0, 0
    constants_errors, course_enrollment_errors, trend_attribution_errors = [], [], []
    for row in csv_reader:
        try:
            num_of_records += 1
            row = utils.convert_csv_row_empty_string_to_none(row)

            institution_identity, branch_symbol = row.get(INSTITUTION_IDENTITY), row.get(BRANCH_SYMBOL)
            student_identity, student_identity_type = row.get(STUDENT_IDENTITY), row.get(STUDENT_IDENTITY_TYPE)
            student_first_name, student_last_name = row.get(STUDENT_FIRST_NAME), row.get(STUDENT_LAST_NAME)
            trend_coordinator_name = row.get(TREND_COORDINATOR_NAME)

            branch_id = Branch.get_branch_id_by_institution_and_symbol(institution_identity, branch_symbol).get('id')
            student_id = get_student(student_identity, student_identity_type, student_first_name,
                                     student_last_name).get(
                'id')

            course_enrollment = create_course_enrollment(row, student_id, branch_id, data_source)
            course_enrollment_success_records += 1

            trend_attribution = create_trend_attribution(row, student_id, course_enrollment.get('id'),
                                                         trend_coordinator_name, data_source)
            second_trend_coordinator_name = row.get(AFTERNOON_TREND_COORDINATOR_NAME)
            if row.get(COURSE_TYPE) in MULTIPLE_DAY_PART_COURSES and second_trend_coordinator_name is not None:
                trend_attribution = create_trend_attribution(row, student_id, course_enrollment.get('id'),
                                                             second_trend_coordinator_name, data_source)
            trend_attribution_success_records += 1
        except exceptions.ConstantNotFound as e:
            row['error'] = str(e)
            course_enrollment_errors.append(row)
        except exceptions.CreateCourseEnrollmentError as e:
            row['error'] = e.message
            course_enrollment_errors.append(row)
        except exceptions.CreateTrendCoordinatorAttributionError as e:
            row['error'] = e.message
            trend_attribution_errors.append(row)
    pop_up_results.append(
        popup_utils.get_popup_record(CourseEnrollment, num_of_records, course_enrollment_success_records,
                                     course_enrollment_errors))
    pop_up_results.append(
        popup_utils.get_popup_record(TrendCoordinationAttribution, num_of_records, trend_attribution_success_records,
                                     trend_attribution_errors))

    return {constants.STR_MESSAGE: None, constants.STR_ERROR: False, 'popup_results': pop_up_results}


def unpack_course_enrollment_trend_attribution(course_enrollment_trend_attribution_list, many=True):
    results = []
    prefix = 'course_enrollment'
    for ce_ta_record in course_enrollment_trend_attribution_list:
        if not ce_ta_record.get('course_enrollments'):
            results.append(ce_ta_record)
            continue
        new_ce_ta_record = ce_ta_record.copy()
        del new_ce_ta_record['course_enrollments']
        for course_enrollment in ce_ta_record['course_enrollments']:
            del course_enrollment['id']
            new_ce_ta_record = {**new_ce_ta_record,
                                **{f"{prefix}_{key}": val for key, val in course_enrollment.items()}}
            results.append(new_ce_ta_record)
    return results if many else results.pop() if results else {}


class CourseEnrollmentTrendCoordinatorAttributionAPI(Resource):

    @login_required()
    def get(self, trend_attribution_id=None, student_id=None):
        if 'csv_template' in request.path:
            try:
                return File.Read.get_csv_template_by_name(COURSE_ENROLLMENT_CSV_PARAMETER)
            except Exception as e:
                print(e)
                return {constants.STR_MESSAGE: messages.REQUEST_FILE_NOT_FOUND_ERROR, constants.STR_ERROR: True}
        if student_id:
            results = TrendCoordinationAttribution.read(many=True, fk_student_id=student_id)
        elif trend_attribution_id:
            results = [TrendCoordinationAttribution.read(many=False, id=trend_attribution_id)]
        else:
            results = TrendCoordinationAttribution.read()
        results = unpack_course_enrollment_trend_attribution(results, many=False if trend_attribution_id else True)
        return jsonify(results)

    @login_required()
    def post(self):
        if request.files and COURSE_ENROLLMENT_CSV_PARAMETER in request.files:
            data_source = UPLOAD_SOURCES[1]
            csv_file = request.files[COURSE_ENROLLMENT_CSV_PARAMETER]
            if not csv_file.filename:
                return {constants.STR_MESSAGE: messages.REQUEST_EMPTY_FILE_ERROR, constants.STR_ERROR: True}
            trend_course_csv = File.Read.read_file(csv_file.read(), csv_file.filename)
            csv_reader = csv.DictReader(trend_course_csv)
            return create_course_enrollment_trend_attribution_from_csv(csv_reader, data_source)
            response[
                'attribution_errors'] = TrendCoordinationAttribution.attribute_trend_coordinator_to_course_enrollment(
                attribution_records)
            return response

        user_json = request.get_json()
        course_enrollment_json = {key[len('course_enrollment_'):]: val for key, val in user_json.items() if
                                  key.startswith("course_enrollment")}
        course_enrollment = CourseEnrollment.create(course_enrollment_json)[constants.STR_DATA]
        trend_attribution_json = {key: val for key, val in user_json.items() if 'course_enrollment' not in key}
        trend_attribution_json['fk_course_enrollment_id'] = course_enrollment.get('id')
        return TrendCoordinationAttribution.create(trend_attribution_json)

    @login_required()
    def put(self, trend_attribution_id):
        user_json = request.get_json()

        course_enrollment_json = {key[len('course_enrollment_'):]: val for key, val in user_json.items() if
                                  key.startswith("course_enrollment")}
        course_enrollment_json['id'] = user_json.get('fk_course_enrollment_id')
        if not user_json.get('fk_course_enrollment_id'):
            CourseEnrollment.create(course_enrollment_json)
        else:
            CourseEnrollment.update(course_enrollment_json, id=user_json.get('fk_course_enrollment_id'))

        trend_attribution_json = {key: val for key, val in user_json.items() if 'course_enrollment' not in key}
        return jsonify(TrendCoordinationAttribution.update(trend_attribution_json, id=trend_attribution_id))

    @login_required()
    def delete(self, trend_attribution_id):
        result = TrendCoordinationAttribution.delete(id=trend_attribution_id)

        if result[constants.STR_ERROR]:
            return jsonify({constants.STR_ERROR: True
                               , constants.STR_MESSAGE: messages.COLUMN_DELETE_FAILED.format(
                    "TrendCoordinationAttribution")})

        return jsonify({constants.STR_ERROR: False
                           , constants.STR_MESSAGE: messages.COLUMN_DELETE_SUCCESSFULLY.format(
                "TrendCoordinationAttribution")})
