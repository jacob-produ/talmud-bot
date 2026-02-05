from core import messages
from school_manager.constants import constants_lists
from school_manager.constants import course_types
from flask import request, jsonify
from flask_restful import Resource
from school_manager.routes.auth import login_required, role_required


class GeneralListsAPI(Resource):
    @staticmethod
    @login_required()
    def get():
        return jsonify({"expense_payment_methods": constants_lists.EXPENSE_PAYMENT_METHODS,
                        "income_payment_methods": constants_lists.INCOME_PAYMENT_METHODS,
                        "income_payment_status": constants_lists.INCOME_PAYMENT_STATUS,
                        "education_payment_status": constants_lists.EDUCATION_INCOME_PAYMENT_STATUS,
                        "course_types": course_types.COURSE_TYPE_MAP,
                        "attributions": constants_lists.ATTRIBUTIONS,
                        "scholarship_types": constants_lists.SCHOLARSHIP_TYPES
                        })
