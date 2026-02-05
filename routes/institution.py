from core import messages
from school_manager.constants import constants
from school_manager.models.institution import Institution
from flask import request, jsonify
from flask_restful import Resource
from school_manager.routes.auth import login_required, role_required


class InstitutionAPI(Resource):
    @login_required()
    def get(self, institution_id=None):
        if institution_id:
            results = Institution.read(many=False, id=institution_id)
        else:
            results = Institution.read()
        return jsonify(results)

    @login_required()
    def post(self):
        user_json = request.get_json()
        dict_error = {}  # TODO: Dict Error

        if "name" not in user_json:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_MANDATORY.format("name")})

        if "identity" not in user_json:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_MANDATORY.format("identity")})

        user_json["name"] = user_json["name"].lower()
        return jsonify(Institution.create(user_json))

    @login_required()
    def put(self, institution_id):
        user_json = request.get_json()
        return jsonify(Institution.update(user_json, id=institution_id))

    @login_required()
    def delete(self, institution_id):
        result = Institution.delete(id=institution_id)

        if result[constants.STR_ERROR]:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_DELETE_FAILED.format("Institution")})

        return jsonify({constants.STR_ERROR: False,
                        constants.STR_MESSAGE: messages.COLUMN_DELETE_SUCCESSFULLY.format("Institution")})
