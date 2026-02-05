from core import messages
from school_manager.constants import constants
from school_manager.models.examiner import Examiner
from flask import request, jsonify
from flask_restful import Resource
from school_manager.routes.auth import login_required, role_required


class ExaminerAPI(Resource):
    @login_required()
    def get(self, examiner_id=None):
        if examiner_id:
            results = Examiner.read(many=False, id=examiner_id)
        else:
            results = Examiner.read()
        return jsonify(results)

    @login_required()
    def post(self):
        user_json = request.get_json()
        dict_error = {}  # TODO: Dict Error

        if "first_name" not in user_json:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_MANDATORY.format("first_name")})

        if "last_name" not in user_json:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_MANDATORY.format("last_name")})

        user_json["first_name"] = user_json["first_name"].lower()
        user_json["last_name"] = user_json["last_name"].lower()

        return jsonify(Examiner.create(user_json))

    @login_required()
    def put(self, examiner_id):
        user_json = request.get_json()
        return jsonify(Examiner.update(user_json, id=examiner_id))

    @login_required()
    def delete(self, examiner_id):
        result = Examiner.delete(id=examiner_id)

        if result[constants.STR_ERROR]:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_DELETE_FAILED.format("Examiner")})

        return jsonify({constants.STR_ERROR: False,
                        constants.STR_MESSAGE: messages.COLUMN_DELETE_SUCCESSFULLY.format("Examiner")})
