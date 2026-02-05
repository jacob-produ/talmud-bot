from core import messages
from school_manager.constants import constants
from school_manager.models.income_source import IncomeSource
from flask import request, jsonify
from flask_restful import Resource
from school_manager.routes.auth import login_required, role_required


class IncomeSourceAPI(Resource):
    @login_required()
    def get(self, income_source_id=None):
        if income_source_id:
            results = IncomeSource.read(many=False, id=income_source_id)
        else:
            results = IncomeSource.read()
        return jsonify(results)

    @login_required()
    def post(self):
        user_json = request.get_json()
        dict_error = {}  # TODO: Dict Error

        if "name" not in user_json:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_MANDATORY.format("name")})

        if "fund_raiser" not in user_json:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_MANDATORY.format("fund_raiser")})

        user_json["name"] = user_json["name"].lower()
        return jsonify(IncomeSource.create(user_json))

    @login_required()
    def put(self, income_source_id):
        user_json = request.get_json()
        return jsonify(IncomeSource.update(user_json, id=income_source_id))

    @login_required()
    def delete(self, income_source_id):
        result = IncomeSource.delete(id=income_source_id)

        if result[constants.STR_ERROR]:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_DELETE_FAILED.format("Income Source")})

        return jsonify({constants.STR_ERROR: False,
                        constants.STR_MESSAGE: messages.COLUMN_DELETE_SUCCESSFULLY.format("Income Source")})
