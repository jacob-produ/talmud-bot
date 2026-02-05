import pandas as pd
import numpy as np
from flask import jsonify, request
from flask_restful import Resource

from school_manager.models.income import Income
from school_manager.models.expense import Expense
from school_manager.models.course_enrollment import CourseEnrollment
from school_manager.models.trend_coordinator_attribution import TrendCoordinationAttribution
# Attribution groups
from school_manager.models.student import Student
from school_manager.models.employee import Employee
from school_manager.models.supplier import Supplier

# Summary groups

from school_manager.routes.finance_report import get_attribution_expenses_and_incomes
from school_manager.constants import finance_report_filters, constants
from school_manager.db import db
from sqlalchemy.sql import func
from sqlalchemy import and_
from datetime import datetime
from school_manager.routes.auth import login_required, role_required

# stubs
from school_manager.stubs import finance_report
from school_manager.stubs import finance_card
from school_manager.stubs import payment_basket


def get_attribution_payments(expense_filters, income_filters):
    expense_filter_list = [finance_report_filters.get_filter_query(f["name"], f["checked"]) for f in expense_filters]
    income_filter_list = [finance_report_filters.get_filter_query(f["name"], f["checked"]) for f in income_filters]

    income_by_month = db.session.query(Income.amount, Income.for_month, Income.fk_institution_id,
                                       Income.fk_trend_coordinator_id).filter(*income_filter_list)
    expense_by_month = db.session.query(Expense.amount, Expense.actual_payment_date, Expense.fk_institution_id,
                                        Expense.fk_trend_coordinator_id).filter(*expense_filter_list)

    income_by_month_pd = pd.read_sql(income_by_month.statement, db.engine)
    expenses_by_month_pd = pd.read_sql(expense_by_month.statement, db.engine)

    income_by_month_pd.dropna(axis=0, inplace=True)
    expenses_by_month_pd.dropna(axis=0, inplace=True)

    payments_by_dates = {income["for_month"].strftime("%d/%m/%Y"): {"income_amount": income["amount"],
                                                                    "expense_amount": None,
                                                                    "fk_institution_id": income["fk_institution_id"],
                                                                    "fk_trend_coordinator_id": income[
                                                                        "fk_trend_coordinator_id"]}
                         for index, income in income_by_month_pd.iterrows()}
    for index, expense in expenses_by_month_pd.iterrows():
        date = expense["actual_payment_date"].strftime("%d/%m/%Y")
        if date in payments_by_dates:
            payments_by_dates[date]["expense_amount"] = expense["amount"]
        else:
            payments_by_dates[date] = {"expense_amount": expense["amount"],
                                       "income_amount": None,
                                       "fk_institution_id": expense["fk_institution_id"],
                                       "fk_trend_coordinator_id": expense["fk_trend_coordinator_id"]}

    return payments_by_dates


def get_student_course_enrollments(student_id):
    course_enrollments_query = db.session.query(CourseEnrollment).filter_by(fk_student_id=student_id)
    trend_attribution_query = db.session.query(TrendCoordinationAttribution).filter_by(fk_student_id=student_id)

    course_enrollments_df = pd.read_sql(course_enrollments_query.statement, db.engine)
    trend_attribution_df = pd.read_sql(trend_attribution_query.statement, db.engine)

    course_enrollments = trend_attribution_df.merge(course_enrollments_df, how='left', right_on=['id'],
                                                     left_on=['fk_course_enrollment_id'],
                                                     suffixes=( '_trend_attribution' ,'_course_enrollment')).fillna(
        np.nan).replace({"NaT": None, np.nan: None})
    return course_enrollments.to_dict(orient="records")


def get_attribution_finance_tables(expense_filters, income_filters):
    current_month, current_year = datetime.today().month, datetime.today().year
    year_start_date_filter, year_end_date_filter = datetime(current_year, 1, 1).strftime("%d/%m/%Y %H:%M"), datetime(
        current_year + 1, 1, 1).strftime("%d/%m/%Y %H:%M")

    month_start_date_filter = datetime(current_year, current_month, 1).strftime("%d/%m/%Y %H:%M")
    month_end_date_filter = datetime(current_year + 1, 1, 1) if current_month == 12 else datetime(current_year,
                                                                                                  current_month + 1, 1)
    month_end_date_filter = month_end_date_filter.strftime("%d/%m/%Y %H:%M")

    income_filters.append({"name": "income_date", "checked": [year_start_date_filter, year_end_date_filter]})
    expense_filters.append({"name": "expense_date", "checked": [year_start_date_filter, year_end_date_filter]})

    yearly = get_attribution_expenses_and_incomes(expense_filters, income_filters)
    yearly["yearly_balance"] = yearly["income_sum"] - yearly["expense_sum"]

    income_filters[1]["checked"] = [month_start_date_filter, month_end_date_filter]
    expense_filters[1]["checked"] = [month_start_date_filter, month_end_date_filter]

    monthly = get_attribution_expenses_and_incomes(expense_filters, income_filters)
    monthly["monthly_balance"] = monthly["income_sum"] - monthly["expense_sum"]
    yearly_expense = float(yearly["expense_sum"][0]) if len(yearly["expense_sum"]) > 0 else 0.0
    yearly_income = float(yearly["income_sum"][0]) if len(yearly["income_sum"]) > 0 else 0.0
    yearly_balance = float(yearly["yearly_balance"][0]) if len(yearly["yearly_balance"]) > 0 else 0.0
    monthly_balance = float(monthly["monthly_balance"][0]) if len(monthly["monthly_balance"]) > 0 else 0.0

    return {"yearly_expense": yearly_expense,
            "yearly_income": yearly_income,
            "yearly_balance": yearly_balance,
            "monthly_balance": monthly_balance}


def get_attribution_finance_card(attribution, attribution_id):
    expense_filters = [{"name": f"fk_{attribution}_id", "checked": [attribution_id]}]

    income_filters = [{"name": f"fk_{attribution}_id", "checked": [attribution_id]}]

    if attribution == 'student':
        exists = db.session.query(Student.id).filter_by(id=attribution_id).scalar() is not None
    elif attribution == 'supplier':
        exists = db.session.query(Supplier.id).filter_by(id=attribution_id).scalar() is not None
    else:
        exists = db.session.query(Employee.id).filter_by(id=attribution_id).scalar() is not None

    if not exists: return {constants.STR_MESSAGE: {
        constants.STR_VALUE: f'No {attribution} with id {attribution_id}'},
        constants.STR_DATA: None, constants.STR_ERROR: True}

    payments_table = get_attribution_payments(expense_filters, income_filters)
    features_tables = get_attribution_finance_tables(expense_filters, income_filters)
    features_tables["payments"] = payments_table
    if attribution.lower() == 'student':
        student_course_enrollments = get_student_course_enrollments(student_id=attribution_id)
        features_tables["course_enrollments"] = student_course_enrollments
    return features_tables


class FinanceCardAPI(Resource):
    @staticmethod
    @login_required()
    def get(attribution=None, attribution_id=None):
        # return finance_card.stub_json
        return jsonify(get_attribution_finance_card(attribution, int(attribution_id)))
