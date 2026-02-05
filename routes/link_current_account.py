from core import messages
from school_manager.constants import constants
from flask import request, jsonify
from flask_restful import Resource
from school_manager.routes.auth import login_required
from school_manager.models.supplier import Supplier
from school_manager.models.student import Student
from school_manager.models.trend_coordinator import TrendCoordinator
from school_manager.models.current_account import CurrentAccount
from school_manager.models.income import Income
from school_manager.models.expense import Expense
from school_manager.models.msv_file import MSVFile
from school_manager.modules.link_current_account.simulate_students import simulate_students
from school_manager.db import db
from datetime import datetime,timedelta
from sqlalchemy import and_
import pandas as pd

LINK_TYPES = ['msv','supplier','student','trend_coordinator']


def get_attribution_by_income_expense_record(record):
    if record.get('fk_student_id'):
        return 'student', record.get('fk_student_id')
    elif record.get('fk_employee_id'):
        return 'employee', record.get('fk_employee_id')
    elif record.get('fk_supplier_id'):
        return 'supplier', record.get('fk_supplier_id')
    return None, None



def get_associated_ca_data(ca_id):
    current_account_data = CurrentAccount.read(many=False, id=ca_id)
    if not current_account_data:
        raise Exception('There is no current account with that id.')
    if not current_account_data.get('is_linked', None):
        raise Exception(messages.NO_LINK_ERROR)

    bank = current_account_data.get('bank_account')[0]
    bank_id = bank.get('id', None)
    current_account_data['fk_bank_account_id'] = bank_id
    del current_account_data['bank_account']

    all_data = {"current_account": current_account_data}

    expense = current_account_data.get('expense', None)
    income = current_account_data.get('income', None)
    if not expense and not income:
        return all_data
    elif expense:
        attribution, attribution_id = get_attribution_by_income_expense_record(expense[0])
    else:
        attribution, attribution_id =  get_attribution_by_income_expense_record(income[0])

    if attribution and attribution_id:
        attribution_data_df = Expense.get_attribution_data(attribution, [attribution_id])
        attribution_data = list(attribution_data_df.T.to_dict().values())[0] if attribution_data_df.shape[0] > 0 else {}

        if expense:
            expense[0]['attribution'] = attribution_data
        else:
            income[0]['attribution'] = attribution_data

    return all_data

class LinkCAAPI(Resource):
    @login_required()
    def get(self, link_type=None, ca_id=None):
        request_url = request.path
        if 'associated' in request_url and ca_id:
            try:
                return jsonify({constants.STR_ERROR: False,
                             constants.STR_DATA: get_associated_ca_data(ca_id)})
            except Exception as e:
                return jsonify({constants.STR_ERROR: True,
                                constants.STR_MESSAGE:str(e)})

        elif 'associated' in request_url and not ca_id:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: "Missing Current Account id"})

        student_test = request.args.get('test', None)

        if link_type == LINK_TYPES[0]:
            msv_amount = request.args.get('amount')
            end_date = datetime.strptime(request.args.get('date'),'%Y-%m-%d')
            start_date = end_date - timedelta(days=15)
            msv_files = db.session.query(MSVFile.id,MSVFile.amount, MSVFile.date)\
                .filter(and_(MSVFile.amount == abs(float(msv_amount)),MSVFile.date.between(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))))

            msv_files_pd = pd.read_sql(msv_files.statement, db.engine)
            try:
                msv_files_pd['date'] = msv_files_pd['date'].dt.strftime('%Y-%m-%d')
                return jsonify(msv_files_pd.to_dict('records'))
            except AttributeError as e:
                return jsonify({constants.STR_ERROR: True,
                         constants.STR_MESSAGE: messages.READ_NO_DATA_FAIL})


        elif link_type == LINK_TYPES[1]:
            return jsonify(Supplier.read(only_columns_list=['id','identity','name']))

        elif link_type == LINK_TYPES[2] and student_test is not None and student_test.lower() == "true":
            students = simulate_students()
            if students is not None:
                return jsonify(students)

            return jsonify({constants.STR_ERROR: False,
                            constants.STR_MESSAGE: messages.SERVER_ERROR})
        elif link_type == LINK_TYPES[2]:
            return jsonify(Student.read(only_columns_list=['id','identity','first_name','last_name']))

        elif link_type == LINK_TYPES[3]:
            return jsonify(TrendCoordinator.read(only_columns_list=['id','name']))

        return jsonify({constants.STR_ERROR: True,
                        constants.STR_MESSAGE: messages.LINK_TYPE_ERROR})




    @login_required()
    def put(self, link_type=None):
        user_json = request.get_json()

        if 'fk_current_account_id' not in user_json:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_MANDATORY.format("fk_current_account_id")})

        fk_current_account_id = user_json.get('fk_current_account_id', None)
        del user_json["fk_current_account_id"]

        if link_type == LINK_TYPES[0]:

            if 'fk_msv_file_id' not in user_json:
                return jsonify({constants.STR_ERROR: True,
                                constants.STR_MESSAGE: messages.COLUMN_MANDATORY.format("fk_msv_file_id")})
            # Adding a new key on the request json named "delete" - to prevent query from sql to get fk_current_account_id in order to remove is_linked
            fk_current_account_id_copy = fk_current_account_id
            delete = user_json.get('delete', None)
            fk_current_account_id = fk_current_account_id if not delete else None

            expense_update = Expense.update(updated_values_dict={'fk_current_account_id':fk_current_account_id},fk_msv_file_id=user_json['fk_msv_file_id'])

            if constants.STR_ERROR not in expense_update or not expense_update[constants.STR_ERROR]:
                if not delete:
                    CurrentAccount.update(updated_values_dict={'is_linked':True}, id=fk_current_account_id)
                else:
                    CurrentAccount.update(updated_values_dict={'is_linked': False}, id=fk_current_account_id_copy)

            return expense_update



        if 'ca_amount' not in user_json:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_MANDATORY.format("ca_amount")})

        is_linked_read = CurrentAccount.read(many=False, id=fk_current_account_id, only_columns_list=['is_linked'])

        if 'is_linked' not in is_linked_read:
            return is_linked_read

        amount = user_json['ca_amount']
        del user_json["ca_amount"]


        if not is_linked_read['is_linked']:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.NO_LINK_ERROR})

        if amount < 0:
            return jsonify(Expense.update(updated_values_dict=user_json,fk_current_account_id=fk_current_account_id))

        return jsonify(Income.update(updated_values_dict=user_json,fk_current_account_id=fk_current_account_id))




