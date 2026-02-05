from core import messages
from school_manager.constants import constants
from school_manager.models.employee import Employee
from flask import request, jsonify
from flask_restful import Resource
from school_manager.routes.auth import login_required, role_required


class EmployeeAPI(Resource):
    @login_required()
    def get(self, employee_id=None):
        if employee_id:
            results = Employee.read(many=False, id=employee_id)
        else:
            results = Employee.read()
        return jsonify(results)

    @login_required()
    def post(self):
        user_json = request.get_json()

        user_json["first_name"] = user_json["first_name"].lower()
        user_json["last_name"] = user_json["last_name"].lower()

        return jsonify(Employee.create(user_json))

    @login_required()
    def put(self, employee_id):
        user_json = request.get_json()
        return jsonify(Employee.update(user_json, id=employee_id))

    @login_required()
    def delete(self, employee_id):
        result = Employee.delete(id=employee_id)

        if result[constants.STR_ERROR]:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_DELETE_FAILED.format("Employee")})

        return jsonify({constants.STR_ERROR: False,
                        constants.STR_MESSAGE: messages.COLUMN_DELETE_SUCCESSFULLY.format("Employee")})
