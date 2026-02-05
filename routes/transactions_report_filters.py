from flask import jsonify
from flask_restful import Resource
from school_manager.constants import transactions_report_filters as tr_filters_const
from school_manager.routes.auth import login_required

class TransactionsReportFiltersAPI(Resource):
    @staticmethod
    @login_required()
    def get():
        return jsonify(tr_filters_const.FILTERS)
