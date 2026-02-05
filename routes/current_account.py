import csv, time
from io import StringIO
from flask import request, jsonify
from core import messages, utils
from flask_restful import Resource
from school_manager.models.current_account import CurrentAccount
from school_manager.constants.constants import NEW_LINE, UT8_WITH_BOM_ENCODING, WINDOWS_1255_ENCODING
from school_manager.constants import constants
from school_manager.routes.auth import login_required, role_required
from school_manager.modules.file.file import File

from school_manager.modules.link_current_account.link_current_account import LinkCurrentAccount
from school_manager.modules import exceptions
from school_manager.modules import popup_utils

import datetime

from school_manager.constants.constants_lists import UPLOAD_SOURCES


CURRENT_ACCOUNT_CSV_PARAMETER = "current_account_csv"
CSV_ROWS_TO_SKIP = 13
MANDATORY_COLUMNS = ["SYMBOL", "INSTITUTION_IDENTITY"]

DATE_COL = "תאריך"
VALUE_DATE_COL = "יום ערך"
TRANSACTION_DESCRIPTION_COL = "תיאור התנועה"
TRANSACTION_AMOUNT_COL = "₪ זכות/חובה"
BALANCE_COL = "₪ יתרה"
REFERENCE_NUMBER_COL = "אסמכתה"
SECOND_REFERENCE_NUMBER_COL = "אסמכתה משני"
COMMENT_COL = "הערה"
TREND_COORDINATOR_NAME_COL = "מנחה"
BANK_ACCOUNT_NUMBER_COL = "מספר חשבון"
BRANCH_NUMBER_COL = "מספר סניף"
BANK_NUMBER_COL = "מספר בנק"
FRONT_IMAGE_LINK = "קישור תמונה קדמית"
REAR_IMAGE_LINK = "קישור תמונה אחורית"
PDF_LINK = "קישור PDF"
CHECK_NUMBER_COL = "מספר צ'אק"

COLS_DTYPES = {
    DATE_COL: "date",
    VALUE_DATE_COL: "date",
    TRANSACTION_DESCRIPTION_COL: "string",
    TRANSACTION_AMOUNT_COL: "float",
    BALANCE_COL: "float",
    REFERENCE_NUMBER_COL : "string",
    SECOND_REFERENCE_NUMBER_COL : "string",
    COMMENT_COL: "string",
}


def get_ba_checking_account(bank_account_id, with_filters, filters):
    if not with_filters:
        message = "There is no checking account to this bank account"
        if bank_account_id is not None:
            result = CurrentAccount.read(many=True, exclude_columns_list=["bank_account", "id"],
                                         fk_bank_account_id=bank_account_id)
        else:
            result = CurrentAccount.read(many=True, exclude_columns_list=["bank_account", "id"])
    else:
        message = "There is no checking account between this dates"
        try:
            start_date, end_date = datetime.datetime.strptime(filters["start_date"],
                                                              '%d/%m/%Y %H:%M'), datetime.datetime.strptime(
                filters["end_date"], '%d/%m/%Y %H:%M')
        except Exception:
            start_date, end_date = datetime.datetime.strptime(filters["start_date"],
                                                              '%d/%m/%Y'), datetime.datetime.strptime(
                filters["end_date"], '%d/%m/%Y')
        if bank_account_id is not None:
            checking_account_df = CurrentAccount.query.filter(CurrentAccount.date.between(start_date, end_date),
                                                              CurrentAccount.fk_bank_account_id == bank_account_id).all()
        else:
            checking_account_df = CurrentAccount.query.filter(CurrentAccount.date.between(start_date, end_date)).all()

        result = CurrentAccount.Schema(many=True, exclude=["bank_account"]).dump(checking_account_df)

    if len(result) == 0:
        result = {constants.STR_MESSAGE: message,
                  constants.STR_DATA: [], constants.STR_ERROR: False}

    return result


def create_current_account(row, bank_account_id, file_name, data_source):
    ca_file_id = f"{file_name} {int(time.time())}"
    current_account_record = dict(date=row.get(DATE_COL), value_date=row.get(VALUE_DATE_COL),
                                  transaction_description=row.get(TRANSACTION_DESCRIPTION_COL),
                                  transaction_amount=row.get(TRANSACTION_AMOUNT_COL),
                                  balance=row.get(BALANCE_COL),
                                  reference_number=row.get(REFERENCE_NUMBER_COL),
                                  second_reference_number=row.get(SECOND_REFERENCE_NUMBER_COL),
                                  comment=row.get(COMMENT_COL),
                                  fk_bank_account_id=bank_account_id,
                                  ca_file_id=ca_file_id,
                                  data_source=data_source)
    current_account = CurrentAccount.create(current_account_record)
    if current_account[constants.STR_ERROR]:
        raise exceptions.CreateCurrentAccountError(message=str(current_account[constants.STR_MESSAGE]))
    return current_account[constants.STR_DATA]


def create_current_account_from_csv(csv_reader, bank_account_id, fk_institution_id, file_name,data_source):
    pop_up_results = []
    num_of_records = 0
    current_account_success_records, link_current_account_success_records = 0,0
    current_account_errors, link_current_account_errors = [], []
    for row in csv_reader:
        num_of_records += 1
        try:
            row = utils.convert_csv_row_empty_string_to_none(row)
            row = utils.convert_csv_row_dtype(row, COLS_DTYPES)

            current_account = create_current_account(row, bank_account_id, file_name, data_source)
            current_account_success_records += 1
            LinkCurrentAccount.link_facade(current_account, fk_institution_id)
            link_current_account_success_records += 1
        except exceptions.CreateCurrentAccountError as e:
            row['error'] = e.message
            current_account_errors.append(row)
        except exceptions.LinkCurrentAccountError as e:
            row['error'] = e.message
            link_current_account_errors.append(row)
        except Exception as e:
            row['error'] = str(e)
            current_account_errors.append(row)
    pop_up_results.append(
        popup_utils.get_popup_record(CurrentAccount, num_of_records, current_account_success_records,
                                     current_account_errors))
    pop_up_results.append(
        popup_utils.get_popup_record(None, num_of_records, link_current_account_success_records,
                                     link_current_account_errors,name='link_current_account', title='קישור רשומת עו"ש'))
    return {constants.STR_MESSAGE: None, constants.STR_ERROR: False, 'popup_results': pop_up_results}


class CurrentAccountAPI(Resource):
    @staticmethod
    @login_required()
    def get(current_account_id=None):
        if 'csv_template' in request.path:
            try:
                return File.Read.get_csv_template_by_name(CURRENT_ACCOUNT_CSV_PARAMETER)
            except Exception as e:
                print(e)
                return {constants.STR_MESSAGE: messages.REQUEST_FILE_NOT_FOUND_ERROR, constants.STR_ERROR: True}

        if current_account_id:
            results = CurrentAccount.read(many=False, id=current_account_id)
        elif not request.args:
            results = CurrentAccount.read()
        else:
            with_filters = False
            filters = None
            if "start_date" in request.args:
                with_filters = True
                filters = {"start_date": request.args.get('start_date'), "end_date": request.args.get('end_date')}
            bank_account_id = request.args.get('bank_account_id') if 'bank_account_id' in request.args else None
            results = get_ba_checking_account(bank_account_id, with_filters, filters)
        return jsonify(results)

    @staticmethod
    @login_required()
    def post():

        # Add from csv file
        if request.files and CURRENT_ACCOUNT_CSV_PARAMETER in request.files:
            data_source = UPLOAD_SOURCES[0]
            current_account_csv_file = request.files[CURRENT_ACCOUNT_CSV_PARAMETER]
            current_account_csv_data = current_account_csv_file

            current_account_csv_data = File.Read.read_file(current_account_csv_data.read(),
                                                           current_account_csv_data.filename,
                                                           without_stringio=True).split(NEW_LINE)
            # Skip the rows that do not contain tabular data
            current_account_csv = StringIO(NEW_LINE.join(current_account_csv_data[CSV_ROWS_TO_SKIP:]))
            try:
                bank_account_id, fk_institution_id = CurrentAccount.get_bank_account_from_csv(
                    current_account_csv_data[:CSV_ROWS_TO_SKIP])
            except Exception as err:
                return jsonify({
                    constants.STR_MESSAGE: str(err), constants.STR_ERROR: True
                })

            csv_reader = csv.DictReader(current_account_csv)
            return create_current_account_from_csv(csv_reader, bank_account_id, fk_institution_id,
                                                  current_account_csv_file.filename.split(".")[0],
                                                   data_source)

        else:
            data_json = request.get_json()
            return jsonify(CurrentAccount.create(data_json))

    @staticmethod
    @login_required()
    def put(current_account_id):
        data_json = request.get_json()
        return jsonify(CurrentAccount.update(data_json, id=current_account_id))

    @staticmethod
    @login_required()
    def delete(current_account_id):
        result = CurrentAccount.delete(id=current_account_id)
        return result
