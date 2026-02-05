import csv

from core import messages, utils
from flask import request, jsonify
from flask_restful import Resource
from school_manager.constants import constants

from school_manager.models.donator import Donator
from school_manager.modules.file.file import File


from school_manager.modules import exceptions
from school_manager.modules import popup_utils

from school_manager.constants.constants_lists import UPLOAD_SOURCES

from school_manager.routes.auth import login_required

DONATOR_CSV_PARAMETER = "donator_csv"

CREDIT_FOUR_DIGITS_COL = "ארבע ספרות אחרונות"
IDENTITY_COL = "תעודת זהות"
FIRST_NAME_COL = "שם פרטי"
LAST_NAME_COL = "שם משפחה"
MAIL_COL = "מייל"
CITY_COL = "עיר"
STREET_COL = "רחוב"
STREET_NUMBER_COL = "מספר רחוב"
STATE = "מדינה"
PHONE = "נייד"
TYPE = "סוג תורם"
NEW_LINE = "\n"

def create_donator(row, data_source):
    first_name, last_name = row.get(FIRST_NAME_COL), row.get(LAST_NAME_COL)
    city, street, street_number = row.get(CITY_COL), row.get(STREET_COL), row.get(STREET_NUMBER_COL)
    identity, last_four_digits = row.get(IDENTITY_COL), row.get(CREDIT_FOUR_DIGITS_COL)
    mail, state, phone, type = row.get(MAIL_COL), row.get(STATE), row.get(PHONE), row.get(TYPE)
    donator_record = dict(first_name=first_name, last_name=last_name, identity=identity,
                        credit_four_digits=last_four_digits,
                        mail=mail, city=city, street=street, street_number=street_number, state=state, phone=phone,
                        type=type, data_source=data_source)

    donator = Donator.create(donator_record)
    if donator[constants.STR_ERROR]:
        raise exceptions.CreateDonatorError(
            message=str(donator[constants.STR_MESSAGE]))
    return donator[constants.STR_DATA]

def create_donator_from_csv(csv_reader, data_source):
    pop_up_results = []
    num_of_records, donator_success_records = 0, 0
    constants_errors, donator_errors = [], []
    for row in csv_reader:

        try:
            num_of_records += 1
            row = utils.convert_csv_row_empty_string_to_none(row)

            donator = create_donator(row, data_source)
            donator_success_records += 1
        except exceptions.ConstantNotFound as e:
            row['error'] = str(e)
            donator_errors.append(row)
        except exceptions.CreateDonatorError as e:
            row['error'] = e.message
            donator_errors.append(row)
    pop_up_results.append(
        popup_utils.get_popup_record(Donator, num_of_records, donator_success_records,
                                     donator_errors))

    return {constants.STR_MESSAGE: None, constants.STR_ERROR: False, 'popup_results': pop_up_results}



class DonatorAPI(Resource):

    @staticmethod
    @login_required()
    def get(donator_id=None):
        if 'csv_template' in request.path:
            try:
                return File.Read.get_csv_template_by_name(DONATOR_CSV_PARAMETER)
            except Exception as e:
                print(e)
                return {constants.STR_MESSAGE: messages.REQUEST_FILE_NOT_FOUND_ERROR, constants.STR_ERROR: True}
        if donator_id:
            results = Donator.read(many=False, id=donator_id)
        else:
            results = Donator.read()
        return jsonify(results)

    @staticmethod
    @login_required()
    def post():
        # Add from csv file
        if request.files and DONATOR_CSV_PARAMETER in request.files:
            data_source = UPLOAD_SOURCES[0]
            donator_file = request.files[DONATOR_CSV_PARAMETER]
            if not donator_file.filename:
                return {constants.STR_MESSAGE: messages.REQUEST_EMPTY_FILE_ERROR, constants.STR_ERROR: True}

            donator_data = File.Read.read_file(donator_file.read(), donator_file.filename)
            check_reader = csv.DictReader(donator_data)
            return create_donator_from_csv(check_reader, data_source)
        else:
            donator_json = request.get_json()
            return jsonify(Donator.create(donator_json))