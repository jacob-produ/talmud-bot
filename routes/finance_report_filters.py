from flask import jsonify, request
from flask_restful import Resource
from school_manager.constants import finance_report_filters as fr_filters_const
from school_manager.routes.auth import login_required, role_required

class FinanceReportFiltersAPI(Resource):
    @staticmethod
    @login_required()
    def get():
        payment_basket = request.args.get('payment_basket')
        if  payment_basket and payment_basket == "true":
            return jsonify(fr_filters_const.PB_FILTERS)
        return jsonify(fr_filters_const.FE_FILTERS)
