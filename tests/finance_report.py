import pandas as pd
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

from school_manager.db import db
from sqlalchemy.sql import func

# income -> method
# expense -> payment_method
# student -> course_type
# student -> identity_type
# expense -> payment_status
# income -> income_source -> xxxx(?) # TODO: CHECK
# student -> eligibility_level # 0 = not eligible

FILTERS = {}

ATTRIBUTION_GROUPS_QUERIES = {"student": db.session.query(Student.id.label('attribution_id'), Student.identity,
                                                          func.concat(Student.first_name, " ", Student.last_name)
                                                          .label("full_name")),
                              "employee":  db.session.query(Employee.id.label('attribution_id'),
                                                            Employee.identity,
                                                            func.concat(Employee.first_name, " ", Employee.last_name)
                                                            .label("full_name")),
                              "supplier": db.session.query(Supplier.id.label('attribution_id'),
                                                           Supplier.identity, Supplier.name.label("full_name"))}


SUMMARY_GROUPS_QUERIES = {"fk_institution_id": db.session.query(Institution.id.label('fk_institution_id'),
                                                                Institution.identity, Institution.name),
                          "fk_branch_id": db.session.query(Branch.id.label('fk_branch_id'), Branch.symbol,
                                                          func.concat(Institution.name, " - ", Branch.symbol)
                                                           .label("name")).join(Branch.institution),
                          "fk_trend_coordinator_id": db.session.query(
                              TrendCoordinator.id.label('fk_trend_coordinator_id'),
                              TrendCoordinator.name)}


def get_summary_total_balance_df(summary_col):
    expense_and_income_total_df = get_single_summary_expenses_and_incomes(summary_col)
    expense_and_income_total_df["balance_total"] = expense_and_income_total_df["income_sum"] - expense_and_income_total_df["expense_sum"]
    return expense_and_income_total_df


def get_single_summary_expenses_and_incomes(summary_col, expense_filters={}, income_filters={}):
    """

    :param summary_col: fk_institution_id / fk_branch_id / fk_trend_coordinator_id
    :param expense_filters:
    :param income_filters:
    :return: data frame of expenses and incomes grouped by the summary col
    """
    expense_sum = db.session.query(getattr(Expense, summary_col), func.sum(Expense.amount).label("expense_sum"))\
        .filter_by(**expense_filters).group_by(getattr(Expense, summary_col))

    income_sum = db.session.query(getattr(Income, summary_col), func.sum(Income.amount).label("income_sum"))\
        .filter_by(**income_filters).group_by(getattr(Income, summary_col))

    expense_pd = pd.read_sql(expense_sum.statement, db.engine)
    income_pd = pd.read_sql(income_sum.statement, db.engine)

    expense_and_income_summary_df = pd.merge(expense_pd, income_pd, on=[summary_col], how='outer').fillna(0)

    return expense_and_income_summary_df


def get_summary_finance_report(expense_filters={}, income_filters={}):
    summary_finance_report = {}
    for summary_col, summary_elements_query in SUMMARY_GROUPS_QUERIES.items():
        summary_total_balance_df = get_summary_total_balance_df(summary_col)
        ex_inc_summary_df = get_single_summary_expenses_and_incomes(summary_col, expense_filters, income_filters)
        group_elements_df = pd.read_sql(summary_elements_query.statement, db.engine)
        ex_inc_summary_df = ex_inc_summary_df.merge(group_elements_df, on=summary_col)
        ex_inc_summary_df["balance"] = ex_inc_summary_df["income_sum"] - ex_inc_summary_df["expense_sum"]

        ex_inc_summary_df = ex_inc_summary_df.merge(summary_total_balance_df, on=summary_col, suffixes=(None, "_total"))
        summary_finance_report[summary_col[3:-3]] = ex_inc_summary_df.to_dict(orient='records')

    return summary_finance_report


def get_attribution_expenses_and_incomes(expense_filters={}, income_filters={}):
    expense_sum = db.session.query(Expense.attribution_id, Expense.attribution, func.sum(Expense.amount).label("expense_sum"))\
        .filter_by(**expense_filters).group_by(Expense.attribution, Expense.attribution_id)

    income_sum = db.session.query(Income.attribution_id, Income.attribution, func.sum(Income.amount).label("income_sum"))\
        .filter_by(**income_filters).group_by(Income.attribution, Income.attribution_id)

    expense_pd = pd.read_sql(expense_sum.statement, db.engine)
    income_pd = pd.read_sql(income_sum.statement, db.engine)

    expense_and_income_pd = pd.merge(expense_pd, income_pd, on=['attribution', 'attribution_id'], how='outer').fillna(0)
    return expense_and_income_pd


def get_attribution_total_balance_df():
    expense_and_income_total_df = get_attribution_expenses_and_incomes()
    expense_and_income_total_df["balance_total"] = expense_and_income_total_df["income_sum"] - expense_and_income_total_df["expense_sum"]
    return expense_and_income_total_df


def get_attribution_finance_report():
    attribution_groups_results = {}
    expense_and_income_total_df = get_attribution_total_balance_df()
    # Filter example
    # expense_and_income_df = get_expenses_and_incomes(expense_filters={'payment_method': 'שיק'})
    expense_and_income_df = get_attribution_expenses_and_incomes()

    # Attribution Groups
    expense_income_grouped = expense_and_income_df.groupby('attribution')
    for group_name, group_query in ATTRIBUTION_GROUPS_QUERIES.items():
        group_elements_df = pd.read_sql(group_query.statement, db.engine)
        group_finance_report = expense_income_grouped.get_group(group_name).merge(group_elements_df, on='attribution_id')
        group_finance_report["balance"] = group_finance_report["income_sum"] - group_finance_report["expense_sum"]
        group_finance_report = group_finance_report.merge(expense_and_income_total_df,
                                                          on=['attribution', 'attribution_id'],
                                                          suffixes=(None, "_total"))
        attribution_groups_results[group_name] = group_finance_report.to_dict(orient="records")
    return attribution_groups_results


def get_finance_report():
    return get_attribution_finance_report(), get_summary_finance_report()


if __name__ == "__main__":
    import datetime
    print(datetime.datetime.now())
    # finance_report = get_finance_report()
    a = get_summary_finance_report()
    print(datetime.datetime.now())
