from flask_restful import Resource
from flask import send_file, request
import school_manager.constants.talmud as tc
from school_manager.routes.auth import login_required
from school_manager.constants.payment_check import PAYMENT_CHECKS_TEMPLATE_FILE_PATH

class DownloadTemplateAPI(Resource):
    @login_required()
    def get(self):
        try:
            action = request.args.get('action')
            if action in (tc.TASK_REMOVE_STUDENTS, tc.TASK_APPROVE_STUDENTS,tc.TASK_REJECT_STUDENTS):
                return send_file(tc.TALMUD_TEMPLATE_FILE_PATH, as_attachment=True, download_name=f"talmud_template.xlsx")
            elif action == tc.TASK_ADD_STUDENTS:
                return send_file(tc.ADD_STUDENTS_TEMPLATE_FILE_PATH, as_attachment=True, download_name=f"add_students_template.xlsx")
            elif action == "payment_checks":
                return send_file(PAYMENT_CHECKS_TEMPLATE_FILE_PATH, as_attachment=True, download_name=f"payment_checks_template.xlsx")
            return None
        except Exception as e:
            return f"Error: {str(e)}", 500
