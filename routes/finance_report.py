import math
import pandas as pd
import numpy as np
from flask import jsonify, request
from flask_restful import Resource

from school_manager.models.income import Income
from school_manager.models.expense import Expense

# Attribution groups
from school_manager.models.student import Student
from school_manager.models.employee import Employee
from school_manager.models.supplier import Supplier

# Summary groups
from school_manager.models.branch import Branch
from school_manager.models.institution import Institution
from school_manager.models.trend_coordinator import TrendCoordinator
from school_manager.models.bank_account import BankAccount

from school_manager.constants import finance_report_filters, constants
from school_manager.db import db
from sqlalchemy.sql import func
from sqlalchemy import and_
from datetime import datetime
from school_manager.routes.auth import login_required, role_required

from school_manager.modules.google_sheet import post_google_sheet_data
# stubs
from school_manager.stubs import finance_report
from school_manager.stubs import finance_card
from school_manager.stubs import payment_basket


# Summary finance report (right table)
def get_summary_groups_queries():
    return {"fk_institution_id": db.session.query(Institution.id.label('fk_institution_id'),
                                                  Institution.identity, Institution.name),
            "fk_branch_id": db.session.query(Branch.id.label('fk_branch_id'), Branch.symbol,
                                             func.concat(Institution.name, " - ", Branch.symbol)
                                             .label("name")).join(Branch.institution),
            "fk_trend_coordinator_id": db.session.query(
                TrendCoordinator.id.label('fk_trend_coordinator_id'),
                TrendCoordinator.name)}


def get_summary_total_balance_df(summary_col):
    expense_and_income_total_df = get_single_summary_expenses_and_incomes(summary_col, expense_filters=[],
                                                                          income_filters=[])
    expense_and_income_total_df["balance_total"] = expense_and_income_total_df["income_sum"] - \
                                                   expense_and_income_total_df["expense_sum"]
    return expense_and_income_total_df


def get_single_summary_expenses_and_incomes(summary_col, expense_filters, income_filters, expense_only=False,
                                            income_only=False):
    """

    :param summary_col: fk_institution_id / fk_branch_id / fk_trend_coordinator_id
    :param expense_filters:
    :param income_filters:
    :return: data frame of expenses and incomes grouped by the summary col
    """
    expense_filter_list = [finance_report_filters.get_filter_query(f["name"], f["checked"]) for f in expense_filters]

    expense_sum = db.session.query(getattr(Expense, summary_col), func.sum(Expense.amount).label("expense_sum")) \
        .filter(*expense_filter_list).group_by(getattr(Expense, summary_col))

    income_filter_list = [finance_report_filters.get_filter_query(f["name"], f["checked"]) for f in income_filters]

    # Join Income.income_source, so we can filter by income_source
    income_sum = db.session.query(getattr(Income, summary_col), func.sum(Income.amount).label("income_sum")) \
        .filter(*income_filter_list) \
        .join(Income.income_source) \
        .group_by(getattr(Income, summary_col))

    expense_pd = pd.read_sql(expense_sum.statement, db.engine)
    expense_pd = expense_pd[expense_pd[getattr(Expense, summary_col).key].notna()]

    income_pd = pd.read_sql(income_sum.statement, db.engine)
    income_pd = income_pd[income_pd[getattr(Income, summary_col).key].notna()]

    if expense_only:
        expense_and_income_summary_df = pd.merge(expense_pd, income_pd, on=[summary_col], how='left').fillna(0)
    elif income_only:
        expense_and_income_summary_df = pd.merge(income_pd, expense_pd, on=[summary_col], how='left').fillna(0)
    else:
        expense_and_income_summary_df = pd.merge(expense_pd, income_pd, on=[summary_col], how='outer').fillna(0)

    return expense_and_income_summary_df


def get_summary_finance_report(expense_filters, income_filters, expense_only=False, income_only=False):
    summary_finance_report = {}
    for summary_col, summary_elements_query in get_summary_groups_queries().items():
        summary_total_balance_df = get_summary_total_balance_df(summary_col)
        ex_inc_summary_df = get_single_summary_expenses_and_incomes(summary_col, expense_filters, income_filters,
                                                                    expense_only=expense_only, income_only=income_only)
        group_elements_df = pd.read_sql(summary_elements_query.statement, db.engine)
        ex_inc_summary_df = ex_inc_summary_df.merge(group_elements_df, on=summary_col)
        ex_inc_summary_df["balance"] = ex_inc_summary_df["income_sum"] - ex_inc_summary_df["expense_sum"]

        ex_inc_summary_df = ex_inc_summary_df.merge(summary_total_balance_df, on=summary_col, suffixes=(None, "_total"))
        # Cut the summary col to remove the fk_ and the _id
        summary_finance_report[summary_col[3:-3]] = ex_inc_summary_df.to_dict(orient='records')

    return summary_finance_report


def get_attribution_group_bank_account(attribution, group=True):
    expense_ba = db.session.query(getattr(Expense, f'fk_{attribution}_id').label('attribution_id'),
                                  func.min(Expense.fk_bank_account_id).label('fk_bank_account_id'),
                                  BankAccount.account_number) \
        .join(BankAccount, BankAccount.id == Expense.fk_bank_account_id) \
        .group_by(getattr(Expense, f'fk_{attribution}_id'), BankAccount.account_number)

    income_ba = db.session.query(getattr(Income, f'fk_{attribution}_id').label('attribution_id'),
                                 func.min(Income.fk_bank_account_id).label('fk_bank_account_id')) \
        .group_by(getattr(Income, f'fk_{attribution}_id'))

    expense_pd = pd.read_sql(expense_ba.statement, db.engine)
    if not group: return expense_pd
    income_pd = pd.read_sql(income_ba.statement, db.engine)
    expense_pd = expense_pd.drop('account_number', axis=1)
    bank_account_pd = pd.concat([expense_pd, income_pd], axis=0).sort_values('fk_bank_account_id',
                                                                             ascending=False).drop_duplicates(
        ['attribution_id'])
    bank_account_pd.replace({np.nan: None}, inplace=True)
    bank_account_pd['attribution_id'] = bank_account_pd['attribution_id'].astype(np.float)
    return bank_account_pd


def get_attribution_groups():
    return ['student', 'employee', 'supplier']


def get_attribution_query(main_model, model_columns, filters=[]):
    fr_attributions = finance_report_filters.ATTRIBUTIONS
    query_columns = model_columns
    query_columns.extend(finance_report_filters.get_attributions_columns())
    # query_models = [main_model, *finance_report_filters.get_attributions_models()]

    query = db.session.query(*query_columns)
    for attribution in fr_attributions:
        model = attribution.get('model')
        query = query.outerjoin(model, getattr(main_model,
                                               attribution.get('join_keys')[0]) == getattr(model,
                                                                                           attribution.get('join_keys')[
                                                                                               1]))
    query.filter(*filters)
    return query


def get_attribution_type(row):

    if row.empty: return None
    if row['fk_student_id'] and not math.isnan(row['fk_student_id']):
        return 'student'
    elif row['fk_employee_id'] and not math.isnan(row['fk_employee_id']):
        return 'employee'
    elif row['fk_supplier_id'] and not math.isnan(row['fk_supplier_id']):
        return 'supplier'
    return 'without'


def group_amount_by_attribution(model_df, is_income=True):
    model_df['attribution_id'] = model_df['fk_student_id'].fillna(model_df['fk_employee_id']).fillna(
        model_df['fk_supplier_id'])
    for field in ['identity', 'full_name', 'payment_method']:
        model_df[field] = model_df[f'student_{field}'].fillna(model_df[f'supplier_{field}']).fillna(
            model_df[f'employee_{field}'])
    model_df['attribution'] = model_df.apply(get_attribution_type, axis=1)
    model_df = model_df[model_df['attribution'] != 'without']
    amount_sum_col_name = 'income_sum' if is_income else 'expense_sum'
    amount_summarized_columns = ['attribution', 'attribution_id', amount_sum_col_name,
                                 'full_name', 'identity', 'payment_method']
    amount_summarized_df = pd.DataFrame(columns=amount_summarized_columns)

    model_df_grouped = model_df.groupby(['attribution', 'attribution_id'], as_index=False)

    for attribute_name, attribute_df in model_df_grouped:
        # reorder columns
        attribute_df[amount_sum_col_name] = attribute_df['amount'].sum()
        attribute_ordered_df = attribute_df[amount_summarized_columns]
        amount_summarized_df = pd.concat([amount_summarized_df, attribute_ordered_df], axis=0)
    return amount_summarized_df


def get_attribution_expenses_and_incomes(expense_filters, income_filters, student_filters=[], group=True):
    expense_filter_list = [finance_report_filters.get_filter_query(f["name"], f["checked"]) for f in expense_filters]
    income_filter_list = [finance_report_filters.get_filter_query(f["name"], f["checked"]) for f in income_filters]

    expense_query = get_attribution_query(Expense,
                                          [Expense.fk_student_id, Expense.fk_employee_id, Expense.fk_supplier_id,
                                           Expense.amount]
                                          , filters=expense_filter_list)
    income_query = get_attribution_query(Income, [Income.fk_student_id, Income.fk_employee_id, Income.fk_supplier_id,
                                                  Income.amount]
                                         , filters=income_filter_list)

    expense_df = pd.read_sql(expense_query.statement, db.engine)
    income_df = pd.read_sql(income_query.statement, db.engine)

    expense_df_grouped = group_amount_by_attribution(expense_df, is_income=False).drop_duplicates()
    income_df_grouped = group_amount_by_attribution(income_df, is_income=True).drop_duplicates()

    income_df_grouped = income_df_grouped[['attribution', 'attribution_id', 'income_sum']]
    expense_and_income_df = pd.merge(expense_df_grouped[expense_df_grouped['attribution_id'].notnull()],
                                     income_df_grouped[income_df_grouped['attribution_id'].notnull()],
                                     on=['attribution', 'attribution_id'], how='outer', suffixes=('', '_in')).fillna(0)
    return expense_and_income_df


def get_attribution_total_balance_df():
    expense_and_income_total_df = get_attribution_expenses_and_incomes(expense_filters=[], income_filters=[])
    expense_and_income_total_df["balance_total"] = expense_and_income_total_df["income_sum"] - \
                                                   expense_and_income_total_df["expense_sum"]
    return expense_and_income_total_df[['attribution', 'attribution_id', 'balance_total', 'income_sum', 'expense_sum']]


def get_attribution_finance_report(expense_filters, income_filters, student_filters, group=True):
    attribution_groups_results = {}
    expense_and_income_total_df = get_attribution_total_balance_df()
    # Filter example
    # expense_and_income_df = get_expenses_and_incomes(expense_filters={'payment_method': 'שיק'})
    expense_and_income_df = get_attribution_expenses_and_incomes(expense_filters, income_filters, student_filters)

    # Attribution Groups
    expense_income_grouped = expense_and_income_df.groupby('attribution')

    for group_name in get_attribution_groups():
        if group_name in expense_income_grouped.groups:
            expense_income_bank_account = get_attribution_group_bank_account(group_name, group=True)

            group_finance_report = expense_income_grouped.get_group(group_name)
            group_finance_report["balance"] = group_finance_report["income_sum"] - group_finance_report["expense_sum"]
            group_finance_report = group_finance_report.merge(expense_income_bank_account, on=['attribution_id'])
            group_finance_report = group_finance_report.merge(expense_and_income_total_df,
                                                              on=['attribution', 'attribution_id'],
                                                              suffixes=(None, "_total"))
            attribution_groups_results[group_name] = group_finance_report.to_dict(orient="records")
        else:
            attribution_groups_results[group_name] = []
    return attribution_groups_results


class FinanceReportAPI(Resource):
    @staticmethod
    @login_required()
    def post():
        import json
        url = request.url
        if 'export' in url:
            request_json = json.loads(request.get_json())
            table = request_json.get('table')
            # tab = request_json.get('tab')
            data = request_json.get('data')
            post_google_sheet_data(table,data)
            return {}
        pay = request.args.get('pay')
        if pay and pay == 'true':
            expenses = []
            for expense in request.get_json():
                attribution = f"fk_{expense.get('attribution').lower()}_id"
                new_expense = dict(internal_system_action=True,**expense)
                new_expense[attribution] = expense['attribution_id']
                new_expense.pop('attribution', None)
                new_expense.pop('attribution_id', None)
                expenses.append(new_expense)
            return Expense.create_ignore(expenses)
        filters = request.get_json()
        # return jsonify(finance_report.stub_json)
        return jsonify(get_attribution_finance_report(filters.get("expense_filters", []),
                                                      filters.get("income_filters", []),
                                                      filters.get("student_filters", [])),
                       get_summary_finance_report(filters.get("expense_filters", []),
                                                  filters.get("income_filters", [])))
