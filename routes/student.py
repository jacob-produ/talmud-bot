import csv
import json
import logging

from core import messages, utils
from school_manager.constants import constants
from school_manager.models.student import Student

from school_manager.models.general_bank_account import GeneralBankAccount
from school_manager.models.student_history import StudentHistory
from flask import request, jsonify
from flask_restful import Resource
from school_manager.routes.auth import login_required
from school_manager.modules.file.file import File

from school_manager.modules.constants_validation import ConstantsValidation
from school_manager.modules import exceptions
from school_manager.modules import popup_utils

from school_manager.constants.constants_lists import UPLOAD_SOURCES

STUDENT_CSV_PARAMETER = "students_csv"

FIRST_NAME = "שם פרטי"
LAST_NAME = "שם משפחה"
IDENTITY = "תעודת זהות"
IDENTITY_TYPE = "סוג זיהוי"
BIRTH_DATE = "תאריך לידה"
MAIN_PHONE_NUMBER = "טלפון ראשי"
SECONDARY_PHONE_NUMBER = "טלפון משני"
STATE = "מדינה"
CITY = "עיר"
STREET = "רחוב"
STREET_NUMBER = "מספר רחוב"
MARTIAL_STATUS = "סטטוס"
FIRST_PARENT_PHONE = "טלפון הורה ראשון"
SECOND_PARENT_PHONE = "טלפון הורה שני"
HOME_PHONE = "טלפון בית"
MAIL = "מייל"
FATHER_NAME = "שם אבא"
PARTNER_NAME = "שם בן זוג"
LANGUAGE = "שפה"
ENTRANCE_COUNTRY_DATE = "תאריך כניסה לארץ"
DEPARTURE_COUNTRY_DATE = "תאריך יציאה מארץ"
SERVICE_STATUS = "סטטוס שירות"


def create_student(row, data_source):
    birth_date = row.get(BIRTH_DATE) if row.get(BIRTH_DATE) else None
    departure_country_date = row.get(DEPARTURE_COUNTRY_DATE) if row.get(DEPARTURE_COUNTRY_DATE) else None
    entrance_country_date = row.get(ENTRANCE_COUNTRY_DATE) if row.get(ENTRANCE_COUNTRY_DATE) else None
    student_record = dict(first_name=row.get(FIRST_NAME), last_name=row.get(LAST_NAME), identity=row.get(IDENTITY),
                          identity_type=row.get(IDENTITY_TYPE), birth_date=birth_date,
                          main_phone_number=row.get(MAIN_PHONE_NUMBER),
                          secondary_phone_number=row.get(SECONDARY_PHONE_NUMBER), state=row.get(STATE),
                          city=row.get(CITY),
                          street=row.get(STREET), street_number=row.get(STREET_NUMBER),
                          marital_status=row.get(MARTIAL_STATUS), first_parent_phone=row.get(FIRST_PARENT_PHONE),
                          second_parent_phone=row.get(SECOND_PARENT_PHONE),
                          mail=row.get(MAIL), father_name=row.get(FATHER_NAME), partner_name=row.get(PARTNER_NAME),
                          language=row.get(LANGUAGE), entrance_country_date=entrance_country_date,
                          departure_country_date=departure_country_date,
                          service_status=row.get(SERVICE_STATUS),home_phone=row.get(HOME_PHONE),
                          data_source=data_source)
    student = Student.create(student_record)
    if student[constants.STR_ERROR]:
        raise exceptions.CreateStudentError(
            message=str(student[constants.STR_MESSAGE]))
    return student[constants.STR_DATA]


def constants_validation(row):
    ConstantsValidation.student_identity_type_validation(row.get(IDENTITY_TYPE))


def create_from_csv(csv_reader, data_source):
    pop_up_results = []
    num_of_records, student_success_records = 0, 0
    constants_errors, student_errors = [], []
    for row in csv_reader:
        try:
            num_of_records += 1
            row = utils.convert_csv_row_empty_string_to_none(row)

            student = create_student(row, data_source)
            student_success_records += 1
        except exceptions.ConstantNotFound as e:
            row['error'] = str(e)
            student_errors.append(row)
        except exceptions.CreateStudentError as e:
            row['error'] = e.message
            student_errors.append(row)
    pop_up_results.append(
        popup_utils.get_popup_record(Student, num_of_records, student_success_records,
                                     student_errors))

    return {constants.STR_MESSAGE: None, constants.STR_ERROR: False, 'popup_results': pop_up_results}
    response = Student.create_ignore(students)
    response['additional_information'] = {'constant_errors': constant_errors}
    return response


class StudentAPI(Resource):
    @login_required()
    def get(self, student_id=None):
        if 'csv_template' in request.path:
            try:
                return File.Read.get_csv_template_by_name(STUDENT_CSV_PARAMETER)
            except Exception as e:
                print(e)
                return {constants.STR_MESSAGE: messages.REQUEST_FILE_NOT_FOUND_ERROR, constants.STR_ERROR: True}

        if student_id:
            bank_results = GeneralBankAccount.read(many=True, attribution_id=student_id, attribution_type="student")
            results = Student.read(many=False, id=student_id)
            results["bank"] = bank_results
        else:
            results = Student.read()
        return jsonify(results)

    @login_required()
    def post(self):
        # Add students from csv file
        if request.files and STUDENT_CSV_PARAMETER in request.files:
            data_source = UPLOAD_SOURCES[0]
            students_csv_file = request.files[STUDENT_CSV_PARAMETER]
            if not students_csv_file.filename:
                return {constants.STR_MESSAGE: messages.REQUEST_EMPTY_FILE_ERROR, constants.STR_ERROR: True}
            students_csv = File.Read.read_file(students_csv_file.read(), students_csv_file.filename)
            csv_reader = csv.DictReader(students_csv)

            return create_from_csv(csv_reader, data_source)
        else:
            student_json = request.get_json()
            return jsonify(Student.create(student_json))

    @login_required()
    def put(self, student_id):
        user_json = request.get_json()
        # update student_history
        student = Student.read(many=False, student_id=student_id)
        student_identity, student_identity_type = student.get('identity'), student.get('identity_type')
        if student_identity and user_json.get('identity') and student_identity != user_json.get(
                'identity') and user_json.get('identity_type') and student_identity_type != user_json.get(
                'identity_type'):
            student_history_dict = dict(fk_student_id=student_id, identity=student_identity,
                                        identity_type=student_identity_type)
            StudentHistory.create(student_history_dict)
        return jsonify(Student.update(user_json, id=student_id))

    @login_required()
    def delete(self, student_id):
        # result = Student.delete(id=student_id)
        result = Student.update(updated_values_dict={"deleted": True}, id=student_id)

        if result[constants.STR_ERROR]:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_DELETE_FAILED.format("Student")})

        return jsonify({constants.STR_ERROR: False,
                        constants.STR_MESSAGE: messages.COLUMN_DELETE_SUCCESSFULLY.format("Student")})
