from flask import jsonify, request
from flask_restful import Resource
from school_manager.constants import reception_basket_filters as rb_filters_const
from school_manager.routes.auth import login_required, role_required

class PeriodicReceptionFiltersAPI(Resource):
    @staticmethod
    @login_required()
    def get():
        return jsonify(rb_filters_const.PR_FILTERS)
