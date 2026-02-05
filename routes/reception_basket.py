import pandas as pd
from flask import jsonify, request
from flask_restful import Resource

from school_manager.models.income import Income
from school_manager.models.expense import Expense

# Attribution groups
from school_manager.models.student import Student


# Summary groups
from school_manager.models.donator import Donator
from school_manager.models.institution import Institution
from school_manager.models.trend_coordinator import TrendCoordinator


from school_manager.constants import reception_basket_filters, constants
from school_manager.db import db
from sqlalchemy.sql import func

from school_manager.routes.auth import login_required, role_required

#stubs
from school_manager.stubs import reception_basket
# TODO: get rid off attribution and attribution_id
# Summary finance report (right table)
def get_summary_groups_queries():
    return {"fk_institution_id": db.session.query(Institution.id.label('fk_institution_id'),
                                                  Institution.identity, Institution.name),
            "fk_donator_id": db.session.query(Donator.id.label('fk_donator_id'), Donator.identity,
                                             func.concat(Donator.first_name, " ", Donator.last_name)
                                             .label("name")),
            "fk_trend_coordinator_id": db.session.query(
                TrendCoordinator.id.label('fk_trend_coordinator_id'),
                TrendCoordinator.name),
            "fk_student_id": db.session.query(
                Student.id.label('fk_student_id'),
                func.concat(Student.first_name, " ", Student.last_name)
                    .label("name")),
            }

def get_summary_total_balance_df(summary_col):
    expense_and_income_total_df = get_single_summary_expenses_and_incomes(summary_col, expense_filters=[],income_filters=[])
    if 'attribution' in summary_col:
        expense_and_income_total_df["income_sum"] = None
        expense_and_income_total_df["expense_sum"] = None
        expense_and_income_total_df["balance_total"] = None
    else:
        expense_and_income_total_df["balance_total"] = expense_and_income_total_df["income_sum"] - expense_and_income_total_df["expense_sum"]
    return expense_and_income_total_df


def get_single_summary_expenses_and_incomes(summary_col, expense_filters, income_filters):

    expense_filter_list = [reception_basket_filters.get_filter_query(f["name"], f["checked"]) for f in expense_filters]
    income_filter_list = [reception_basket_filters.get_filter_query(f["name"], f["checked"]) for f in income_filters]

    income_sum = db.session.query(getattr(Income, summary_col), func.sum(Income.amount).label("income_sum")) \
        .filter(*income_filter_list) \
        .join(Income.income_source) \
        .group_by(getattr(Income, summary_col))

    income_pd = pd.read_sql(income_sum.statement, db.engine)
    income_pd = income_pd[income_pd[getattr(Income, summary_col).key].notna()]

    if 'donator' not in summary_col:
        expense_sum = db.session.query(getattr(Expense, summary_col), func.sum(Expense.amount).label("expense_sum")) \
            .filter(*expense_filter_list).group_by(getattr(Expense, summary_col))
        expense_pd = pd.read_sql(expense_sum.statement, db.engine)
        expense_pd = expense_pd[expense_pd[getattr(Expense, summary_col).key].notna()]
        expense_and_income_summary_df = pd.merge(expense_pd, income_pd, on=[summary_col], how='outer').fillna(0)
    else:
        expense_and_income_summary_df = income_pd
        expense_and_income_summary_df['expense_sum'] = 0

    return expense_and_income_summary_df



def get_summary_reception_basket(income_filters):
    summary_finance_report = {}
    for summary_col, summary_elements_query in get_summary_groups_queries().items():
        summary_filter_df = get_single_summary_expenses_and_incomes(summary_col, expense_filters=[],income_filters=income_filters)
        summary_filter_df = summary_filter_df.drop(['expense_sum','income_sum'], axis=1)
        summary_total_balance_df = get_summary_total_balance_df(summary_col)
        summary_total_balance_df = summary_total_balance_df.merge(summary_filter_df,
                                                                      on=summary_col)
        group_elements_df = pd.read_sql(summary_elements_query.statement, db.engine)
        ex_inc_summary_df = summary_total_balance_df.merge(group_elements_df, on=summary_col, suffixes=(None, "_total"))

        summary_finance_report[summary_col[3:-3]] = ex_inc_summary_df.to_dict(orient='records')


    return summary_finance_report

# Attribution finance report (left table)
def get_donator():
    donator_query = db.session.query(Donator.id.label('fk_donator_id'), Donator.identity,
                                        func.concat(Donator.first_name, " ", Donator.last_name)
                                        .label("full_name"))
    return pd.read_sql(donator_query.statement, db.engine)

def get_income(income_filters):
    income_filter_list = [reception_basket_filters.get_filter_query(f["name"], f["checked"]) for f in income_filters]
    income_sum = db.session.query(Income.id.label('income_id'), Income.fk_student_id.label('attribution_id'),
                                  Income.fk_institution_id,Income.fk_trend_coordinator_id,
                                  Income.fk_donator_id,Income.transmission_date,
                                  Income.for_month,Income.amount,
                                  Income.method,Income.is_printable) \
        .filter(*income_filter_list) \
        .join(Income.income_source)
    income_pd = pd.read_sql(income_sum.statement, db.engine)
    income_pd['attribution'] = 'attribution'
    return income_pd

def get_donator_reception_basket(income_filters):
    donations_result = {}
    donators_df = get_donator()
    income_df = get_income(income_filters)

    income_donator_df = income_df.merge(donators_df, on=['fk_donator_id'])
    if income_donator_df.shape[0]:
        income_donator_df['for_month'] = income_donator_df['for_month'].dt.strftime('%Y-%m-%dT%H:%M:%S')
        income_donator_df['transmission_date'] = income_donator_df['transmission_date'].dt.strftime('%Y-%m-%dT%H:%M:%S')
    donations_result['donations'] = income_donator_df.to_dict(orient='records')
    return donations_result


def get_reception_basket(income_filters):

    income_filters.append({"name": "income_payment_status","checked": ["טיוטה"]})
    # right table
    summary_report = get_summary_reception_basket(income_filters)
    # left table
    attribution_report = get_donator_reception_basket(income_filters)


    return attribution_report,summary_report



class ReceptionBasketAPI(Resource):
    @staticmethod
    @login_required()
    def post():
        filters = request.get_json()
        return jsonify(get_reception_basket(filters.get("income_filters", [])))
        # return jsonify(reception_basket.stub_json)
