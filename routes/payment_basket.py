import math
import pandas as pd
import numpy as np
from flask import jsonify, request
from flask_restful import Resource
from school_manager.db import db
from school_manager.models.expense import Expense
from school_manager.routes.auth import login_required, role_required
from school_manager.routes.finance_report import get_summary_finance_report, get_attribution_query, \
    get_attribution_total_balance_df, get_attribution_groups, get_attribution_group_bank_account,get_attribution_type
from school_manager.constants import finance_report_filters, constants


def get_attribution_expenses(expense_filters):
    expense_filter_list = [finance_report_filters.get_filter_query(f["name"], f["checked"]) for f in expense_filters]

    expense_query = get_attribution_query(Expense, [Expense.id.label('expense_id'), Expense.fk_student_id,
                                                    Expense.fk_employee_id, Expense.fk_supplier_id,
                                                    Expense.amount.label("expense_sum"), Expense.payment_method,
                                                    Expense.transmission_date,Expense.fk_trend_coordinator_id,
                                                    Expense.for_month,Expense.fk_branch_id,Expense.merged_printing_number,
                                                    Expense.is_printable]
                                          , filters=expense_filter_list)

    expense_df = pd.read_sql(expense_query.statement, db.engine)
    expense_df['attribution_id'] = expense_df['fk_student_id'].fillna(expense_df['fk_employee_id']).fillna(
        expense_df['fk_supplier_id'])
    expense_df['attribution'] = expense_df.apply(get_attribution_type, axis=1)
    for field in ['identity', 'full_name', 'payment_method']:
        expense_df[field] = expense_df[f'student_{field}'].fillna(expense_df[f'supplier_{field}']).fillna(
            expense_df[f'employee_{field}'])

    # change dates format
    for col in expense_df.columns:
        if expense_df[col].dtype == 'datetime64[ns]':
            expense_df[col] = expense_df[col].dt.strftime('%Y-%m-%dT%H:%M:%S')

    expense_df["expense_id"] = expense_df["expense_id"].astype(np.int64)
    expense_df = expense_df[['expense_id','attribution_id','attribution',
                             'expense_sum', 'payment_method', 'transmission_date', 'for_month',
                             'is_printable','course_enrollment_id','student_payment_method',
                              'identity', 'full_name','fk_trend_coordinator_id','fk_branch_id','merged_printing_number']]

    return expense_df.fillna(0)


def get_attribution_payment_basket(expense_filters, student_filters):
    attribution_groups_results = {}
    expense_and_income_total_df = get_attribution_total_balance_df()
    # Filter example
    expense_and_income_df = get_attribution_expenses(expense_filters)

    # Attribution Groups
    expense_income_grouped = expense_and_income_df.groupby('attribution')

    for group_name in get_attribution_groups():
        if group_name in expense_income_grouped.groups:
            expense_income_bank_account = get_attribution_group_bank_account(group_name, group=True)

            group_finance_report = expense_income_grouped.get_group(group_name)
            group_finance_report = group_finance_report.merge(expense_income_bank_account, on=['attribution_id'])
            group_finance_report = group_finance_report.merge(expense_and_income_total_df,
                                                              on=['attribution', 'attribution_id'],
                                                              suffixes=(None, "_total"))
            attribution_groups_results[group_name] = group_finance_report.to_dict(orient="records")
        else:
            attribution_groups_results[group_name] = []
    return attribution_groups_results


def del_fields_report(summary_report, fields):
    for key, val in summary_report.items():
        for attribute in val:
            for field in fields:
                if field in attribute:
                    attribute.pop(field)
    return summary_report


def get_payment_basket(expense_filters, student_filters):
    expense_filters = [filter for filter in expense_filters if "date" not in filter]
    student_filters = [filter for filter in student_filters if "date" not in filter]

    expense_filters.append({"name": "expense_payment_status", "checked": ["טיוטה"]})
    summary_report_fields_to_remove = ['balance', 'income_sum', 'income_sum_total']
    attribution_report_fields_to_remove = ['attribution', 'expense_sum_total', 'income_sum', 'income_sum_total']
    # right table
    summary_report = del_fields_report(get_summary_finance_report(expense_filters, [], expense_only=True),
                                       summary_report_fields_to_remove)

    # left table
    attribution_report = del_fields_report(get_attribution_payment_basket(expense_filters, student_filters),
                                           attribution_report_fields_to_remove)

    return attribution_report, summary_report


class PaymentBasketAPI(Resource):
    @staticmethod
    @login_required()
    def post():
        filters = request.get_json()
        return jsonify(get_payment_basket(filters.get("expense_filters", []), filters.get("student_filters", [])))
