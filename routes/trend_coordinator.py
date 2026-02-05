from core import messages, utils
from school_manager.constants import constants
from school_manager.models.trend_coordinator import TrendCoordinator

from flask import request, jsonify
from flask_restful import Resource
from school_manager.routes.auth import login_required


from school_manager.modules.file.file import File
from school_manager.modules.constants_validation import ConstantsValidation
from school_manager.modules import exceptions
from school_manager.modules import popup_utils
import csv

from school_manager.constants.constants_lists import UPLOAD_SOURCES

from school_manager.modules.google_sheet import get_google_sheet_data


GOOGLE_SHEET_PARAMETER = "google_sheet"
GOOGLE_SHEET_NAME = "trend_coordinator"
TREND_COORDINATOR_CSV_PARAMETER = "trend_coordinator_csv"

NAME = "שם מנחה"
CREATED_BY_USER = "נוצר על ידי"
STUDY_FRAMEWORK = "מסגרת לימודים"
STUDY_PROGRAM = "תכנית לימוד"
PROFESSION = "התמחות"
DONE_BY_USER = "בוצע על ידי"
EDUCATION = "השכלה"
CITY = "עיר"
STREET = "רחוב"
STREET_NUMBER = "מספר רחוב"
HOME_CITY = "עיר בית"
HOME_STREET = "רחוב בית"
HOME_STREET_NUMBER = "מספר רחוב בית"
MAIL = "מייל"
PHONE = "טלפון"
SECOND_PHONE = "טלפון נוסף"
FIRST_OPENING_HOUR = "תחילת שעת פעילות ראשונה"
FIRST_CLOSING_HOUR = "סוף שעת פעילות ראשונה"
SECOND_OPENING_HOUR = "תחילת שעת פעילות שנייה"
SECOND_CLOSING_HOUR = "סוף שעת פעילות שנייה"
EXAMINER_NAME = "אחראי בחינות"
DEFAULT_PAYMENT_METHOD = "שיטת תשלום דיפולטיבית"
CONTACT_NAME = "שם איש קשר"
CONTACT_PHONE = "טלפון איש קשר"
COORDINATION_MIDDLEMAN_NAME = "אחראי תיאום"
EXCELLENCE_SCHOLARSHIP = "מלגת תוספת מנחה"
BASE_SCHOLARSHIP = "מילגת בסיס"
TEST_SCHOLARSHIP = "מלגת מבחן"
TEACHING_SCHOLARSHIP = "מלגת לימוד"
SCHOLARSHIP_METHOD = "שיטת מלגה"
ELIGIBILITY_MIN = "זכאות מינימאלית"
ELIGIBILITY_METHOD = "שיטת זכאות"
ELIGIBILITY_LEVEL = "רמת זכאות"
PLATFORM_FEE = "עמלת פלטפורמה"
TARGET_AUDIENCE = "קהל יעד"
GOOGLE_SHEET_URL = "כתובת גוגל שיטס"
PASSWORD = "סיסמה"
PERSONAL_CODE = "קוד אישי"
STUDY_HOURS_RANGE = "שעות עבודה"

def create_trend_coordinator(row, data_source):
    trend_coordinator_record = dict(name=row.get(NAME), created_by_user=row.get(CREATED_BY_USER),
                                    study_framework=row.get(STUDY_FRAMEWORK), study_program=row.get(STUDY_PROGRAM),
                                    profession=row.get(PROFESSION), done_by_user=row.get(DONE_BY_USER),
                                    education=row.get(EDUCATION),
                                    city=row.get(CITY), street=row.get(STREET),
                                    street_number=row.get(STREET_NUMBER),
                                    home_city=row.get(HOME_CITY), home_street=row.get(HOME_STREET),
                                    home_street_number=row.get(HOME_STREET_NUMBER),
                                    mail=row.get(MAIL), phone=row.get(PHONE), second_phone=row.get(SECOND_PHONE),
                                    first_opening_hour=row.get(FIRST_OPENING_HOUR),
                                    first_closing_hour=row.get(FIRST_CLOSING_HOUR),
                                    second_opening_hour=row.get(SECOND_OPENING_HOUR),
                                    second_closing_hour=row.get(SECOND_CLOSING_HOUR),
                                    examiner_name=row.get(EXAMINER_NAME),
                                    coordination_middleman_name=row.get(COORDINATION_MIDDLEMAN_NAME),
                                    excellence_scholarship=row.get(EXCELLENCE_SCHOLARSHIP),
                                    base_scholarship=row.get(BASE_SCHOLARSHIP),
                                    test_scholarship=row.get(TEST_SCHOLARSHIP),
                                    teaching_scholarship=row.get(TEACHING_SCHOLARSHIP),
                                    eligibility_min=row.get(ELIGIBILITY_MIN),
                                    eligibility_method=row.get(ELIGIBILITY_METHOD),
                                    eligibility_level=row.get(ELIGIBILITY_LEVEL),
                                    platform_fee=row.get(PLATFORM_FEE),
                                    target_audience=row.get(TARGET_AUDIENCE),
                                    scholarship_method=row.get(SCHOLARSHIP_METHOD),
                                    default_payment_method=row.get(DEFAULT_PAYMENT_METHOD),
                                    google_sheet_url=row.get(GOOGLE_SHEET_URL),
                                    password=row.get(PASSWORD),
                                    personal_code=row.get(PERSONAL_CODE),
                                    data_source=data_source,
                                    study_hourse_range=row.get(STUDY_HOURS_RANGE))
    trend_coordinator = TrendCoordinator.create(trend_coordinator_record)
    if trend_coordinator[constants.STR_ERROR]:
        raise exceptions.CreateTrendCoordinatorError(message=str(trend_coordinator[constants.STR_MESSAGE]))
    return trend_coordinator[constants.STR_DATA]

def update_trend_coordinator(row, data_source):
    trend_coordinator_record = dict(name=row.get(NAME), created_by_user=row.get(CREATED_BY_USER),
                                    study_framework=row.get(STUDY_FRAMEWORK), study_program=row.get(STUDY_PROGRAM),
                                    profession=row.get(PROFESSION), done_by_user=row.get(DONE_BY_USER),
                                    education=row.get(EDUCATION),
                                    city=row.get(CITY), street=row.get(STREET),
                                    street_number=row.get(STREET_NUMBER),
                                    home_city=row.get(HOME_CITY), home_street=row.get(HOME_STREET),
                                    home_street_number=row.get(HOME_STREET_NUMBER),
                                    mail=row.get(MAIL), phone=row.get(PHONE), second_phone=row.get(SECOND_PHONE),
                                    first_opening_hour=row.get(FIRST_OPENING_HOUR),
                                    first_closing_hour=row.get(FIRST_CLOSING_HOUR),
                                    second_opening_hour=row.get(SECOND_OPENING_HOUR),
                                    second_closing_hour=row.get(SECOND_CLOSING_HOUR),
                                    examiner_name=row.get(EXAMINER_NAME),
                                    coordination_middleman_name=row.get(COORDINATION_MIDDLEMAN_NAME),
                                    excellence_scholarship=row.get(EXCELLENCE_SCHOLARSHIP),
                                    base_scholarship=row.get(BASE_SCHOLARSHIP),
                                    test_scholarship=row.get(TEST_SCHOLARSHIP),
                                    teaching_scholarship=row.get(TEACHING_SCHOLARSHIP),
                                    eligibility_min=row.get(ELIGIBILITY_MIN),
                                    eligibility_method=row.get(ELIGIBILITY_METHOD),
                                    eligibility_level=row.get(ELIGIBILITY_LEVEL),
                                    platform_fee=row.get(PLATFORM_FEE),
                                    target_audience=row.get(TARGET_AUDIENCE),
                                    scholarship_method=row.get(SCHOLARSHIP_METHOD),
                                    default_payment_method=row.get(DEFAULT_PAYMENT_METHOD),
                                    google_sheet_url=row.get(GOOGLE_SHEET_URL),
                                    password=row.get(PASSWORD),
                                    personal_code=row.get(PERSONAL_CODE),
                                    data_source=data_source,
                                    study_hourse_range=row.get(STUDY_HOURS_RANGE))
    trend_coordinator = TrendCoordinator.update(trend_coordinator_record,name=row.get(NAME))
    if trend_coordinator[constants.STR_ERROR]:
        raise exceptions.UpdateTrendCoordinatorError(message=str(trend_coordinator[constants.STR_MESSAGE]))
    return trend_coordinator[constants.STR_DATA]

def create_trend_coordinator_from_csv(csv_reader,data_source):
    pop_up_results = []
    num_of_records, trend_coordinator_success_records = 0, 0
    trend_coordinator_errors = []
    for row in csv_reader:
        row = utils.convert_csv_row_empty_string_to_none(row)
        num_of_records += 1
        try:
            ConstantsValidation.scholarship_method_validation(row.get(SCHOLARSHIP_METHOD))
            ConstantsValidation.income_payment_method_validation(row.get(DEFAULT_PAYMENT_METHOD))
            ConstantsValidation.study_hours_range_validation(row.get(STUDY_HOURS_RANGE))
            trend_coordinator = create_trend_coordinator(row, data_source)
            trend_coordinator_success_records += 1
        except exceptions.ConstantNotFound as e:
            row['error'] = str(e)
            trend_coordinator_errors.append(row)
        except exceptions.CreateTrendCoordinatorError as e:
            row['error'] = e.message
            trend_coordinator_errors.append(row)
    pop_up_results.append(
        popup_utils.get_popup_record(TrendCoordinator, num_of_records, trend_coordinator_success_records, trend_coordinator_errors))

    return {constants.STR_MESSAGE: None, constants.STR_ERROR: False, 'popup_results': pop_up_results}


def update_trend_coordinator_from_csv(csv_reader, data_source):
    pop_up_results = []
    num_of_records, trend_coordinator_success_records = 0, 0
    trend_coordinator_errors = []
    for row in csv_reader:
        row = utils.convert_csv_row_empty_string_to_none(row)
        num_of_records += 1
        try:
            trend_coordinator = update_trend_coordinator(row, data_source)
            trend_coordinator_success_records += 1
        except exceptions.ConstantNotFound as e:
            row['error'] = str(e)
            trend_coordinator_errors.append(row)
        except exceptions.UpdateTrendCoordinatorError as e:
            row['error'] = e.message
            trend_coordinator_errors.append(row)
    pop_up_results.append(
        popup_utils.update_popup_record(TrendCoordinator, num_of_records, trend_coordinator_success_records,
                                     trend_coordinator_errors))

    return {constants.STR_MESSAGE: None, constants.STR_ERROR: False, 'popup_results': pop_up_results}


def get_new_records_update_records(csv_reader):
    new_records, existing_records = [], []
    trend_coordinators = TrendCoordinator.read(only_columns_list=['name'], many=True)
    trend_coordinators = set([trend['name'] for trend in trend_coordinators])
    for row in csv_reader:
        if row.get(NAME) in trend_coordinators:
            existing_records.append(row)
        else:
            new_records.append(row)
    return new_records, existing_records

class TrendCoordinatorAPI(Resource):
    @login_required()
    def get(self, trend_coordinator_id=None):
        if 'csv_template' in request.path:
            try:
                return File.Read.get_csv_template_by_name(TREND_COORDINATOR_CSV_PARAMETER)
            except Exception as e:
                print(e)
                return {constants.STR_MESSAGE: messages.REQUEST_FILE_NOT_FOUND_ERROR, constants.STR_ERROR: True}

        if trend_coordinator_id:
            results = TrendCoordinator.read(many=False, id=trend_coordinator_id)
        else:
            results = TrendCoordinator.read()
        return jsonify(results)

    @login_required()
    def post(self):
        params = request.form
        if GOOGLE_SHEET_PARAMETER in params and params[GOOGLE_SHEET_PARAMETER]:
            data_source = UPLOAD_SOURCES[1]
            check_reader = get_google_sheet_data(GOOGLE_SHEET_PARAMETER)
            return create_trend_coordinator_from_csv(check_reader, data_source)
        elif request.files and TREND_COORDINATOR_CSV_PARAMETER in request.files:
            data_source = UPLOAD_SOURCES[0]
            csv_file = request.files[TREND_COORDINATOR_CSV_PARAMETER]
            if not csv_file.filename:
                return {constants.STR_MESSAGE: messages.REQUEST_EMPTY_FILE_ERROR, constants.STR_ERROR: True}

            trend_csv = File.Read.read_file(csv_file.read(), csv_file.filename)
            csv_reader = csv.DictReader(trend_csv)
            return create_trend_coordinator_from_csv(csv_reader, data_source)

        user_json = request.get_json()
        dict_error = {}  # TODO: Dict Error

        if "name" not in user_json:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_MANDATORY.format("name")})

        if "created_by_user" not in user_json:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_MANDATORY.format("created_by_user")})

        if "study_program" not in user_json:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_MANDATORY.format("study_program")})

        if "profession" not in user_json:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_MANDATORY.format("profession")})

        if "done_by_user" not in user_json:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_MANDATORY.format("done_by_user")})

        if "education" not in user_json:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_MANDATORY.format("education")})

        if "eligibility_method" not in user_json:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_MANDATORY.format("eligibility_method")})

        if "eligibility_level" not in user_json:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_MANDATORY.format("eligibility_level")})

        user_json["name"] = user_json["name"].lower()

        return jsonify(TrendCoordinator.create(user_json))

    @login_required()
    def put(self, trend_coordinator_id=None):
        params = request.form
        if GOOGLE_SHEET_PARAMETER in params and params[GOOGLE_SHEET_PARAMETER] or \
                request.files and TREND_COORDINATOR_CSV_PARAMETER in request.files:
            if GOOGLE_SHEET_PARAMETER in params and params[GOOGLE_SHEET_PARAMETER]:
                # data_source
                print('here')
                csv_reader = get_google_sheet_data(GOOGLE_SHEET_PARAMETER)
                # return create_trend_coordinator_from_csv(check_reader)
            elif request.files and TREND_COORDINATOR_CSV_PARAMETER in request.files:
                csv_file = request.files[TREND_COORDINATOR_CSV_PARAMETER]
                if not csv_file.filename:
                    return {constants.STR_MESSAGE: messages.REQUEST_EMPTY_FILE_ERROR, constants.STR_ERROR: True}
                trend_csv = File.Read.read_file(csv_file.read(), csv_file.filename)
                csv_reader = csv.DictReader(trend_csv)
            new_records, update_records = get_new_records_update_records(csv_reader)
            created_records = create_trend_coordinator_from_csv(new_records)
            updated_records = update_trend_coordinator_from_csv(update_records)
            created_records['popup_results'].append(updated_records['popup_results'][0])
            return created_records
        user_json = request.get_json()
        return jsonify(TrendCoordinator.update(user_json, id=trend_coordinator_id))

    @login_required()
    def delete(self, trend_coordinator_id):
        result = TrendCoordinator.delete(id=trend_coordinator_id)

        if result[constants.STR_ERROR]:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_DELETE_FAILED.format("Trend Coordinator")})

        return jsonify({constants.STR_ERROR: False,
                        constants.STR_MESSAGE: messages.COLUMN_DELETE_SUCCESSFULLY.format("Trend Coordinator")})
