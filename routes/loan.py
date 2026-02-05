from core import messages
from school_manager.constants import constants
from school_manager.models.loan import Loan
from flask import request, jsonify
from flask_restful import Resource
from school_manager.routes.auth import login_required, role_required


class LoanAPI(Resource):
    @login_required()
    def get(self, loan_id=None):
        if loan_id:
            results = Loan.read(many=False, id=loan_id)
        else:
            results = Loan.read()
        return jsonify(results)

    @login_required()
    def post(self):
        user_json = request.get_json()
        dict_error = {}  # TODO: Dict Error

        if "account_id" not in user_json:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_MANDATORY.format("account_id")})

        if "total_amount" not in user_json:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_MANDATORY.format("total_amount")})

        if "monthly_amount" not in user_json:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_MANDATORY.format("monthly_amount")})

        if "annual_interest" not in user_json:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_MANDATORY.format("annual_interest")})

        if "lender" not in user_json:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_MANDATORY.format("lender")})

        return jsonify(Loan.create(user_json))

    @login_required()
    def put(self, loan_id):
        user_json = request.get_json()
        return jsonify(Loan.update(user_json, id=loan_id))

    @login_required()
    def delete(self, loan_id):
        result = Loan.delete(id=loan_id)

        if result[constants.STR_ERROR]:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_DELETE_FAILED.format("Loan")})

        return jsonify({constants.STR_ERROR: False,
                        constants.STR_MESSAGE: messages.COLUMN_DELETE_SUCCESSFULLY.format("Loan")})
