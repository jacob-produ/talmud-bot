from core import messages
from school_manager.constants import constants
from school_manager.models.expense import Expense
from flask import request, jsonify,Response
from flask_restful import Resource
from school_manager.routes.auth import login_required, role_required


class ExpenseAPI(Resource):
    @login_required()
    def get(self, expense_id=None, current_account_id=None):
        if expense_id:
            results = Expense.read(many=False, id=expense_id)
        elif current_account_id:
            results = Expense.read(many=False, fk_current_account_id=current_account_id)
        else:
            results = Expense.read()
        return jsonify(results)

    @login_required()
    def post(self):
        request_path = request.path.split("/")
        user_json = request.get_json()
        if request_path[-1] == "print_payment":
            user_json = request.get_json() if type(user_json) == list else []
            zip_data, zip_name = Expense.export_draft(user_json)
            return Response(zip_data, headers={
                'Content-Type': 'application/zip',
                'Content-Disposition': 'attachment; filename=%s;' % zip_name
            })
        elif request_path[-1] == "merge_payment":
            user_json = request.get_json() if type(user_json) == list else []
            unmerge_expenses = Expense.merge_payment(user_json)
            if unmerge_expenses:
                return jsonify({constants.STR_ERROR: True,
                                constants.STR_MESSAGE: messages.MERGE_PAYMENT_ERROR,
                                constants.STR_DATA: unmerge_expenses})
            return jsonify({constants.STR_ERROR: False,
                            constants.STR_MESSAGE: messages.MERGE_PAYMENT_SUCCESS,
                            constants.STR_DATA: unmerge_expenses})
        elif request_path[-1] == "split_payment":
            user_json = request.get_json() if type(user_json) == list else []
            Expense.split_payment(user_json)
            return jsonify({constants.STR_ERROR: False,
                            constants.STR_MESSAGE: messages.SPLIT_PAYMENT_SUCCESS,
                            constants.STR_DATA: None})
        if type(user_json) == list:
            return jsonify(Expense.create_ignore(user_json, with_commit=True))
        else:
            return jsonify(Expense.create(user_json, with_commit=True))

    @login_required()
    def put(self, expense_id):
        user_json = request.get_json()
        return jsonify(Expense.update(user_json, id=expense_id))

    @login_required()
    def delete(self, expense_id=None):
        user_json = request.get_json()
        if not expense_id and type(user_json)== list:
            return jsonify(Expense.delete_ignore(user_json))

        result = Expense.delete(id=expense_id)

        if result[constants.STR_ERROR]:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_DELETE_FAILED.format("Expense")})

        return jsonify({constants.STR_ERROR: False,
                            constants.STR_MESSAGE: messages.COLUMN_DELETE_SUCCESSFULLY.format("Expense")})
