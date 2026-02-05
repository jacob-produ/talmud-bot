import pandas as pd
from pandas.api.types import is_datetime64_any_dtype as is_datetime
import numpy as np
import math
from flask import jsonify, request
from flask_restful import Resource

from school_manager.models.income import Income
from school_manager.models.income_source import IncomeSource
from school_manager.models.expense import Expense
from school_manager.models.msv_file import MSVFile
# Attribution groups
from school_manager.models.student import Student
from school_manager.models.employee import Employee
from school_manager.models.supplier import Supplier

# Summary groups
from school_manager.models.branch import Branch
from school_manager.models.institution import Institution
from school_manager.models.trend_coordinator import TrendCoordinator
from school_manager.models.course_enrollment import CourseEnrollment
from school_manager.models.trend_coordinator_attribution import TrendCoordinationAttribution
from school_manager.models.bank_account import BankAccount

from school_manager.constants import transactions_report_filters
from school_manager.constants.constants_lists import EXPENSE_PAYMENT_STATUS
from school_manager.db import db
from sqlalchemy.sql import func
from sqlalchemy import and_
from datetime import datetime
from school_manager.routes.auth import login_required, role_required

# stubs
from school_manager.stubs import transaction_report


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


def get_single_summary_expenses_and_incomes(summary_col, expense_filters, income_filters):
    expense_filter_list = [transactions_report_filters.get_filter_query(f["name"], f["checked"]) for f in
                           expense_filters]

    expense_sum = db.session.query(getattr(Expense, summary_col), func.sum(Expense.amount).label("expense_sum")) \
        .filter(*expense_filter_list).group_by(getattr(Expense, summary_col))

    income_filter_list = [transactions_report_filters.get_filter_query(f["name"], f["checked"]) for f in income_filters]

    # Join Income.income_source, so we can filter by income_source
    income_sum = db.session.query(getattr(Income, summary_col), func.sum(Income.amount).label("income_sum")) \
        .filter(*income_filter_list) \
        .join(Income.income_source) \
        .group_by(getattr(Income, summary_col))

    expense_pd = pd.read_sql(expense_sum.statement, db.engine)
    expense_pd = expense_pd[expense_pd[getattr(Expense, summary_col).key].notna()]

    income_pd = pd.read_sql(income_sum.statement, db.engine)
    income_pd = income_pd[income_pd[getattr(Income, summary_col).key].notna()]

    expense_and_income_summary_df = pd.merge(expense_pd, income_pd, on=[summary_col], how='outer').fillna(0)

    return expense_and_income_summary_df


def get_summary_finance_report(expense_filters, income_filters):
    summary_finance_report = {}
    for summary_col, summary_elements_query in get_summary_groups_queries().items():
        summary_total_balance_df = get_summary_total_balance_df(summary_col)
        ex_inc_summary_df = get_single_summary_expenses_and_incomes(summary_col, expense_filters, income_filters)
        group_elements_df = pd.read_sql(summary_elements_query.statement, db.engine)
        ex_inc_summary_df = ex_inc_summary_df.merge(group_elements_df, on=summary_col)
        ex_inc_summary_df["balance"] = ex_inc_summary_df["income_sum"] - ex_inc_summary_df["expense_sum"]

        ex_inc_summary_df = ex_inc_summary_df.merge(summary_total_balance_df, on=summary_col, suffixes=(None, "_total"))
        ex_inc_summary_df = ex_inc_summary_df.drop(
            ['expense_sum', 'expense_sum_total', 'income_sum', 'income_sum_total'], axis=1)
        # Cut the summary col to remove the fk_ and the _id
        summary_finance_report[summary_col[3:-3]] = ex_inc_summary_df.to_dict(orient='records')

    return summary_finance_report


def get_expense_data(expense_filters):
    expense_filter_list = [transactions_report_filters.get_filter_query(f["name"], f["checked"]) for f in
                           expense_filters]
    query = db.session.query(Expense.id, Expense.fk_student_id, Expense.fk_supplier_id, Expense.fk_employee_id,
                             Expense.actual_payment_date.label("transaction_date"),
                             Expense.payment_status, Expense.amount, Expense.payment_method, Expense.for_month,
                             Expense.check_printing_date, Expense.fk_msv_file_id,
                             Expense.fk_institution_id.label("transaction_institution_id"),
                             Expense.fk_branch_id.label("transaction_branch_id"),
                             Expense.fk_trend_coordinator_id.label("transaction_trend_coordinator_id")) \
        .filter(*expense_filter_list)
    return pd.read_sql(query.statement, db.engine)


def get_income_data(income_filters):
    income_filter_list = [transactions_report_filters.get_filter_query(f["name"], f["checked"]) for f in income_filters]
    query = db.session.query(Income.id, Income.fk_student_id, Income.fk_supplier_id, Income.fk_employee_id,
                             Income.deposit_date.label("transaction_date"),
                             Income.amount, Income.method.label("payment_method"), Income.for_month,
                             Income.fk_institution_id.label("transaction_institution_id"),
                             Income.fk_branch_id.label("transaction_branch_id"),
                             Income.fk_trend_coordinator_id.label("transaction_trend_coordinator_id")) \
        .join(IncomeSource, IncomeSource.id == Income.fk_income_source_id) \
        .filter(*income_filter_list)
    return pd.read_sql(query.statement, db.engine)


def get_msv_data(msv_ids):
    query = db.session.query(MSVFile.id.label('fk_msv_file_id'), MSVFile.date.label('msv_file_date')).filter(
        MSVFile.id.in_(msv_ids))
    return pd.read_sql(query.statement, db.engine)


def convert_to_iso(df, date_columns):
    print(df.dtypes)
    for col in date_columns:
        df[col] = df[col].apply(lambda date: date.isoformat() if date else date)
        df[col] = df[col].fillna(np.nan).replace({np.nan: None})
        df[col] = df[col].replace({"NaT": None})
    return df


def get_attribution_type(row):
    if row.empty: return None
    if row['fk_student_id'] and not math.isnan(row['fk_student_id']):
        return 'student'
    elif row['fk_employee_id'] and not math.isnan(row['fk_employee_id']):
        return 'employee'
    elif row['fk_supplier_id'] and not math.isnan(row['fk_supplier_id']):
        return 'supplier'
    return 'without'


def get_expense_income_data(expense_filters, income_filters):
    expense_df = get_expense_data(expense_filters)
    msv_df = get_msv_data(expense_df['fk_msv_file_id'].dropna().unique())
    expense_df = expense_df.merge(msv_df, on=['fk_msv_file_id'], how='left')
    expense_df.replace({np.nan: None}, inplace=True)
    expense_df['amount'] = expense_df['amount'] * -1
    expense_df['check_printing_date'] = expense_df['check_printing_date'].replace({None: ''}).astype(str)
    expense_df['msv_file_date'] = expense_df['msv_file_date'].replace({None: ''}).astype(str)
    expense_df['printing_date'] = expense_df['msv_file_date'] + expense_df['check_printing_date']
    expense_df['printing_date'] = expense_df['printing_date'].mask(expense_df['printing_date'] == '', None)
    expense_df['printing_date'] = pd.to_datetime(expense_df['printing_date'], format="%Y-%m-%d %H:%M:%S",
                                                 errors='ignore')
    expense_df.replace({np.nan: None}, inplace=True)

    income_df = get_income_data(income_filters)
    income_df['payment_status'] = None
    income_df['printing_date'] = None
    expense_income_df = pd.DataFrame()
    for col in income_df.columns:
        expense_income_df[col] = pd.concat([expense_df[col], income_df[col]], ignore_index=True)
    expense_income_df['attribution'] = expense_income_df.apply(lambda row: get_attribution_type(row), axis=1)
    expense_income_df['attribution_id'] = expense_income_df['fk_student_id'].fillna(
        expense_income_df['fk_employee_id']).fillna(
        expense_income_df['fk_supplier_id'])
    return convert_to_iso(expense_income_df, ['for_month', 'printing_date', 'transaction_date'])


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


# Attribution finance report (left table)
def get_attribution_groups_queries():
    return {"student": db.session.query(Student.id.label('attribution_id'), Student.identity,
                                        func.concat(Student.first_name, " ", Student.last_name)
                                        .label("full_name"), CourseEnrollment.fk_branch_id, Branch.fk_institution_id,
                                        TrendCoordinationAttribution.fk_trend_coordinator_id, Student.deleted)
        .join(Student, TrendCoordinationAttribution.fk_student_id == Student.id)
        .join(CourseEnrollment, CourseEnrollment.fk_student_id == Student.id)
        .join(Branch, Branch.id == CourseEnrollment.fk_branch_id),
            "employee": db.session.query(Employee.id.label('attribution_id'),
                                         Employee.identity,
                                         func.concat(Employee.first_name, " ", Employee.last_name)
                                         .label("full_name"),
                                         Employee.fk_institution_id),
            "supplier": db.session.query(Supplier.id.label('attribution_id'),
                                         Supplier.identity, Supplier.name.label("full_name")),
            "without": None}


def get_attribution_finance_report(expense_filters, income_filters):
    attribution_groups_results = {}
    expense_and_income_df = get_expense_income_data(expense_filters, income_filters)
    expense_and_income_df = expense_and_income_df.where(pd.notnull(expense_and_income_df), None)
    # Attribution Groups
    expense_income_grouped = expense_and_income_df.groupby('attribution')
    for group_name, group_query in get_attribution_groups_queries().items():
        if group_name in expense_income_grouped.groups:
            if group_name == 'without':
                group_finance_report = expense_income_grouped.get_group(group_name)
            else:
                group_elements_df = pd.read_sql(group_query.statement, db.engine).drop_duplicates()
                expense_income_bank_account = get_attribution_group_bank_account(group_name)
                group_elements_df['attribution'] = group_name
                expense_income_bank_account['attribution'] = group_name
                group_finance_report = expense_income_grouped.get_group(group_name) \
                    .merge(expense_income_bank_account, on=['attribution', 'attribution_id']) \
                    .merge(group_elements_df, on=['attribution', 'attribution_id'])
            group_finance_report["heb_attribution"] = transactions_report_filters.ATTRIBUTION_ENG_HEB.get(group_name)
            attribution_groups_results[group_name] = group_finance_report.to_dict(orient="records")
        else:
            attribution_groups_results[group_name] = []
    return attribution_groups_results


def add_attribution_filters(attribution_filters, expense_filters, income_filters):
    if not attribution_filters:
        return expense_filters, income_filters

    checked_list = attribution_filters[0]['checked']
    expense_filters.append({'name': 'expense_attribution_filters', 'checked': checked_list})
    income_filters.append({'name': 'income_attribution_filters', 'checked': checked_list})
    return expense_filters, income_filters


def check():
    query = db.session.query(MSVFile.id, MSVFile.date)
    return pd.read_sql(query.statement, db.engine)


class TransactionsReportAPI(Resource):
    @staticmethod
    @login_required()
    def post():
        filters = request.get_json()
        expense_filters, income_filters = add_attribution_filters(filters.get("attribution_filters", []),
                                                                  filters.get("expense_filters", []),
                                                                  filters.get("income_filters", []))
        return jsonify(get_attribution_finance_report(expense_filters, income_filters),
                       get_summary_finance_report(expense_filters, income_filters))
        # return jsonify({},
        #                get_summary_finance_report(expense_filters, income_filters))

    @staticmethod
    @login_required()
    def put():
        expense_json = request.get_json()
        results = []
        for expense_id in expense_json.get('expense_ids', []):
            results.append(Expense.update({'payment_status': EXPENSE_PAYMENT_STATUS[0]}, id=expense_id))
        return jsonify(results)
