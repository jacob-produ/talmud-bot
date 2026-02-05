from core import messages
from school_manager.constants import constants
from school_manager.models.exam import Exam
from flask import request, jsonify
from flask_restful import Resource
from school_manager.routes.auth import login_required, role_required


class ExamAPI(Resource):
    @login_required()
    def get(self, exam_id=None):
        if exam_id:
            results = Exam.read(many=False, id=exam_id)
        else:
            results = Exam.read()
        return jsonify(results)

    @login_required()
    def post(self):
        user_json = request.get_json()
        dict_error = {} # TODO: Dict Error
        if "date" not in user_json:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_MANDATORY.format("date")})

        if "examiner_id" not in user_json:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_MANDATORY.format("examiner_id")})

        if "student_id" not in user_json:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_MANDATORY.format("student_id")})

        if "exam_result" not in user_json:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_MANDATORY.format("exam_result")})

        if "exam_number" not in user_json:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_MANDATORY.format("exam_number")})

        return jsonify(Exam.create(user_json))

    @login_required()
    def put(self, exam_id):
        user_json = request.get_json()
        return jsonify(Exam.update(user_json, id=exam_id))

    @login_required()
    def delete(self, exam_id):
        result = Exam.delete(id=exam_id)

        if result[constants.STR_ERROR]:
            return jsonify({constants.STR_ERROR: True,
                            constants.STR_MESSAGE: messages.COLUMN_DELETE_FAILED.format("Exam")})

        return jsonify({constants.STR_ERROR: False,
                        constants.STR_MESSAGE: messages.COLUMN_DELETE_SUCCESSFULLY.format("Exam")})
