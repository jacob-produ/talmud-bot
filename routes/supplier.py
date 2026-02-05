from core import messages, utils
from school_manager.constants import constants
from school_manager.models.supplier import Supplier
from flask import request, jsonify
from flask_restful import Resource
from school_manager.routes.auth import login_required
from school_manager.modules.file.file import File

from school_manager.modules import exceptions
from school_manager.modules import popup_utils

from school_manager.constants.constants_lists import UPLOAD_SOURCES

import csv


SUPPLIER_CSV_PARAMETER = "supplier_csv"


NAME_COL = "שם"
IDENTITY_COL = "מזהה"
BANK_NUMBER_COL = "מספר בנק"
BRANCH_NUMBER_COL = "מספר סניף"
BANK_ACCOUNT_NUMBER_COL = "מספר חשבון"
PHONE_COL = "טלפון"
MAIL_COL = "מייל"
AGENT_COL = "שם סוכן"
AGENT_PHONE_COL = "טלפון סוכן"
CLASSIFICATION_COL = "תחום"


def create_supplier(row, data_source):
    identity = row.get(IDENTITY_COL)
    supplier = Supplier.read(identity=identity, many=False)
    if supplier.get('id'): return supplier


    supplier_record = dict(name=row.get(NAME_COL), identity=identity, phone_number=row.get(PHONE_COL),
                               mail=row.get(MAIL_COL), agent_name=row.get(AGENT_COL),
                               agent_phone=row.get(AGENT_PHONE_COL),
                               classification=row.get(CLASSIFICATION_COL),
                           data_source=data_source)

    supplier = Supplier.create(supplier_record)
    if supplier[constants.STR_ERROR]:
        raise exceptions.CreateSupplierError(
            message=str(supplier[constants.STR_MESSAGE]))
    return supplier[constants.STR_DATA]



def create_supplier_from_csv(csv_reader, data_source):
    pop_up_results = []
    num_of_records, supplier_success_records = 0, 0
    constants_errors, supplier_errors = [], []
    for row in csv_reader:
        try:
            num_of_records += 1
            row = utils.convert_csv_row_empty_string_to_none(row)

            supplier = create_supplier(row, data_source)
            supplier_success_records += 1
        except exceptions.ConstantNotFound as e:
            row['error'] = str(e)
            supplier_errors.append(row)
        except exceptions.CreateSupplierError as e:
            row['error'] = e.message
            supplier.append(row)
    pop_up_results.append(
        popup_utils.get_popup_record(Supplier, num_of_records, supplier_success_records,
                                     supplier_errors))

    return {constants.STR_MESSAGE: None, constants.STR_ERROR: False, 'popup_results': pop_up_results}



class SupplierAPI(Resource):


    @login_required()
    def get(self, supplier_id=None):
        if 'csv_template' in request.path:
            try:
                return File.Read.get_csv_template_by_name(SUPPLIER_CSV_PARAMETER)
            except Exception as e:
                print(e)
                return {constants.STR_MESSAGE: messages.REQUEST_FILE_NOT_FOUND_ERROR, constants.STR_ERROR: True}

        if supplier_id:
            results = Supplier.read(many=False, id=supplier_id)
        else:
            results = Supplier.read()
        return jsonify(results)

    @login_required()
    def post(self):
        # Add from csv file
        if request.files and SUPPLIER_CSV_PARAMETER in request.files:
            data_source = UPLOAD_SOURCES[0]
            csv_file = request.files[SUPPLIER_CSV_PARAMETER]
            if not csv_file.filename:
                return {constants.STR_MESSAGE: messages.REQUEST_EMPTY_FILE_ERROR, constants.STR_ERROR: True}

            csv_data = File.Read.read_file(csv_file.read(), csv_file.filename)
            csv_reader = csv.DictReader(csv_data)
            return create_supplier_from_csv(csv_reader, data_source)

        user_json = request.get_json()
        dict_error = {}  # TODO: Dict Error
        if "name" not in user_json:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_MANDATORY.format("name")})
        if "identity" not in user_json:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_MANDATORY.format("identity")})
        if "classification" not in user_json:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_MANDATORY.format("classification")})
        user_json["name"] = user_json["name"].lower()

        return jsonify(Supplier.create(user_json))

    @login_required()
    def put(self, supplier_id):
        user_json = request.get_json()
        return jsonify(Supplier.update(user_json, id=supplier_id))

    @login_required()
    def delete(self, supplier_id):
        result = Supplier.delete(id=supplier_id)

        if result[constants.STR_ERROR]:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_DELETE_FAILED.format("Supplier")})

        return jsonify({constants.STR_ERROR: False,
                        constants.STR_MESSAGE: messages.COLUMN_DELETE_SUCCESSFULLY.format("Supplier")})
