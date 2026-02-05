import pandas as pd
import numpy as np
from flask import jsonify, request
from flask_restful import Resource

from school_manager.models.periodic_reception import PeriodicReception
from school_manager.models.income import Income
from school_manager.models.expense import Expense

# Attribution groups
from school_manager.models.student import Student
from school_manager.models.employee import Employee
from school_manager.models.supplier import Supplier

# Summary groups
from school_manager.models.donator import Donator
from school_manager.models.branch import Branch
from school_manager.models.institution import Institution
from school_manager.models.trend_coordinator import TrendCoordinator
from school_manager.models.bank_account import BankAccount

from school_manager.constants import reception_basket_filters, constants
from school_manager.constants.constants_lists import INCOME_PAYMENT_STATUS
from school_manager.db import db
from sqlalchemy.sql import func
from sqlalchemy import and_
from datetime import datetime
from school_manager.routes.auth import login_required, role_required

# stubs
from school_manager.stubs import periodic_reception_report


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
                Student.id.label('fk_student_id'), Student.identity,
                func.concat(Student.first_name, " ", Student.last_name)
                    .label("name"))
            }


def get_summary_periodic_reception(summary_col, pr_filters):
    pr_filter_list = [reception_basket_filters.get_filter_query(f["name"], f["checked"]) for f in pr_filters]

    pr_group = db.session.query(getattr(PeriodicReception, summary_col),
                                func.sum(PeriodicReception.amount).label("pr_amount_sum"),
                                func.count(PeriodicReception.id).label("pr_num")) \
        .filter(*pr_filter_list).group_by(getattr(PeriodicReception, summary_col))

    periodic_reception_pd = pd.read_sql(pr_group.statement, db.engine)
    periodic_reception_pd = periodic_reception_pd[
        periodic_reception_pd[getattr(PeriodicReception, summary_col).key].notna()]

    return periodic_reception_pd


def get_summary_reception_report(pr_filters):
    summary_pr_report = {}
    for summary_col, summary_elements_query in get_summary_groups_queries().items():
        summary_filter_df = get_summary_periodic_reception(summary_col, pr_filters=pr_filters)
        group_elements_df = pd.read_sql(summary_elements_query.statement, db.engine)
        ex_inc_summary_df = summary_filter_df.merge(group_elements_df, on=summary_col, suffixes=(None, "_total"))
        summary_pr_report[summary_col[3:-3]] = ex_inc_summary_df.to_dict(orient='records')
    return summary_pr_report


def get_donator():
    donator_query = db.session.query(Donator.id.label('fk_donator_id'), Donator.identity,
                                     func.concat(Donator.first_name, " ", Donator.last_name)
                                     .label("full_name"))
    return pd.read_sql(donator_query.statement, db.engine)


def get_periodic_reception(pr_filters):
    pr_filter_list = [reception_basket_filters.get_filter_query(f["name"], f["checked"]) for f in pr_filters]
    pr_query = db.session.query(PeriodicReception.id, PeriodicReception.charge_date,
                                PeriodicReception.comment, PeriodicReception.periodic_reception_status,
                                PeriodicReception.amount, PeriodicReception.payment_method, PeriodicReception.charges,
                                PeriodicReception.bank_permission_start_date,
                                PeriodicReception.bank_permission_end_date,
                                PeriodicReception.last_charge_date, PeriodicReception.fk_trend_coordinator_id,
                                PeriodicReception.fk_institution_id,
                                PeriodicReception.fk_donator_id, PeriodicReception.fk_student_id).filter(
        *pr_filter_list)

    return pd.read_sql(pr_query.statement, db.engine)


def get_income():
    income_query = db.session.query(Income.payment_status, Income.method, Income.amount,
                                    Income.fk_periodic_reception_id).filter(Income.fk_periodic_reception_id != None)
    return pd.read_sql(income_query.statement, db.engine)


def get_success_failed_pr(pr_row, income_df):
    success_payment = income_df[(income_df['fk_periodic_reception_id'] == pr_row['id']) & (
                income_df['payment_status'] == INCOME_PAYMENT_STATUS[2])]
    failed_payment = income_df[(income_df['fk_periodic_reception_id'] == pr_row['id']) & (
            income_df['payment_status'] == INCOME_PAYMENT_STATUS[3])]
    print(success_payment)
    print(failed_payment)
    return success_payment.shape[0], failed_payment.shape[0]


def get_attribution_reception_report(pr_filters):
    pr_result = {}
    donator_df = get_donator()
    periodic_reception_df = get_periodic_reception(pr_filters)
    income_df = get_income()
    periodic_reception_donator_df = periodic_reception_df.merge(donator_df, on='fk_donator_id')
    periodic_reception_donator_df[['num_success_payment','num_failed_payment']] = \
        periodic_reception_donator_df.apply(lambda row: get_success_failed_pr(row,income_df),result_type='expand', axis='columns')
    periodic_reception_donator_df['charges_remainder'] = periodic_reception_donator_df['charges'] - periodic_reception_donator_df['num_success_payment']
    periodic_reception_donator_df['total_charged_amount'] = periodic_reception_donator_df['amount']*periodic_reception_donator_df['num_success_payment']

    periodic_reception_donator_df['last_charge_date'] = periodic_reception_donator_df['last_charge_date'].dt.strftime('%Y-%m-%dT%H:%M:%S')
    periodic_reception_donator_df['bank_permission_end_date'] = periodic_reception_donator_df['bank_permission_end_date'].dt.strftime(
        '%Y-%m-%dT%H:%M:%S')
    periodic_reception_donator_df['bank_permission_start_date'] = periodic_reception_donator_df['bank_permission_start_date'].dt.strftime(
        '%Y-%m-%dT%H:%M:%S')
    pr_result['periodic_reception'] = periodic_reception_donator_df.replace({np.nan: None}).to_dict(orient='records')
    return pr_result


class PeriodicReceptionReportAPI(Resource):

    @staticmethod
    @login_required()
    def post():
        filters = request.get_json()
        attribution_reception, summary_reception = get_attribution_reception_report(
            filters.get("pr_filters", [])), get_summary_reception_report(filters.get("pr_filters", []))
        return jsonify(attribution_reception, summary_reception)
        # return jsonify(periodic_reception_report.stub_json)
