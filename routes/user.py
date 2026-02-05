from core import messages
from school_manager.constants import constants
from school_manager.models.user import User
from flask import request, jsonify
from flask_restful import Resource
from werkzeug.security import generate_password_hash
from school_manager.routes.auth import login_required, role_required


class UserAPI(Resource):
    @login_required()
    def get(self, user_id=None):
        if user_id:
            results = User.read(many=False, id=user_id, deleted=False)
        else:
            results = User.read(deleted=False)
        return jsonify(results)

    @role_required([constants.ROLE_ADMIN])
    def post(self):
        user_json = request.get_json()
        user_json["username"] = user_json["username"].lower()
        if "password" in user_json.keys():
            user_json["password"] = generate_password_hash(user_json["password"])
        user_json["deleted"] = False

        return jsonify(User.create(user_json))

    @role_required([constants.ROLE_ADMIN])
    def put(self, user_id):
        user_json = request.get_json()
        if "password" in user_json.keys():
            user_json["password"] = generate_password_hash(user_json["password"])
        if "username" in user_json.keys():
            del user_json["username"]

        return jsonify(User.update(user_json, id=user_id))

    @role_required([constants.ROLE_ADMIN])
    def delete(self, user_id):
        result = User.update({"deleted": True}, id=user_id)

        if result[constants.STR_ERROR]:
            return jsonify({constants.STR_ERROR: True
                               , constants.STR_MESSAGE: messages.COLUMN_DELETE_FAILED.format("User")})

        return jsonify({constants.STR_ERROR: False
                           , constants.STR_MESSAGE: messages.COLUMN_DELETE_SUCCESSFULLY.format("User")})
