from werkzeug.security import generate_password_hash
from school_manager.db import db
import pandas as pd
from dateutil.relativedelta import relativedelta
from datetime import datetime
from core import messages
from school_manager.constants import constants
from school_manager.models.bank_account import BankAccount
from school_manager.models.institution import Institution
from school_manager.models.current_account import CurrentAccount
from school_manager.models.loan import Loan
from school_manager.models.expense import Expense
from school_manager.models.income import Income
from flask import request, jsonify
from flask_restful import Resource
from sqlalchemy import func, or_, and_
from school_manager.routes.auth import login_required, role_required


def get_bank_account_commitments(bank_account_pd, cash=False):
    if not cash:
        commitments = db.session.query(Expense.fk_bank_account_id, func.sum(Expense.amount).label("amount")) \
            .filter(or_(Expense.payment_status == "הודפס", Expense.payment_status == "נמסר"),
                    and_(Expense.payment_method == "הוראת קבע", Expense.payment_status == "טיוטה")) \
            .group_by(Expense.fk_bank_account_id).order_by(Expense.fk_bank_account_id)
    else:
        commitments = db.session.query(Expense.fk_bank_account_id, func.sum(Expense.amount).label("amount")) \
            .filter(or_(Expense.payment_status == "הודפס", Expense.payment_status == "נמסר",
                        Expense.payment_status == "טיוטה")).group_by(
            Expense.fk_bank_account_id).order_by(Expense.fk_bank_account_id)

    commitments_pd = pd.read_sql(commitments.statement, db.engine)
    bank_account_pd['id'], commitments_pd['fk_bank_account_id'] = pd.to_numeric(bank_account_pd['id']), pd.to_numeric(
        commitments_pd['fk_bank_account_id'])
    return bank_account_pd.merge(commitments_pd, how='left', right_on='fk_bank_account_id',
                                 left_on='id')["amount"]


def get_bank_account_monthly_commitments(bank_account_pd):
    tenth_of_next_month = datetime(year=datetime.today().year, month=datetime.today().month, day=11) + relativedelta(
        months=1)
    six_month_before = datetime.today() - relativedelta(months=6)
    commitments = db.session.query(Expense.fk_bank_account_id, func.sum(Expense.amount).label("amount")) \
        .filter(and_(Expense.transmission_date < tenth_of_next_month.isoformat(),
                     or_(and_(Expense.payment_method == "שיק",
                              Expense.transmission_date > six_month_before.isoformat()),
                         Expense.payment_method != "שיק"))) \
        .group_by(Expense.fk_bank_account_id).order_by(Expense.fk_bank_account_id)

    commitments_pd = pd.read_sql(commitments.statement, db.engine)
    bank_account_pd['id'], commitments_pd['fk_bank_account_id'] = pd.to_numeric(bank_account_pd['id']), pd.to_numeric(
        commitments_pd['fk_bank_account_id'])
    return bank_account_pd.merge(commitments_pd, how='left', right_on='fk_bank_account_id',
                                 left_on='id')["amount"]


def get_bank_account_balances(bank_account_pd):
    balances = db.session.query(CurrentAccount.id, CurrentAccount.fk_bank_account_id, CurrentAccount.balance) \
        .filter(CurrentAccount.id.in_(
        db.session.query(func.max(CurrentAccount.id), ).group_by(CurrentAccount.fk_bank_account_id))) \
        .order_by(CurrentAccount.fk_bank_account_id)

    balances_pd = pd.read_sql(balances.statement, db.engine)
    bank_account_pd['id'], balances_pd['fk_bank_account_id'] = pd.to_numeric(bank_account_pd['id']), pd.to_numeric(
        balances_pd['fk_bank_account_id'])

    return \
        bank_account_pd.merge(balances_pd.drop('id', axis=1), how='left', right_on='fk_bank_account_id', left_on='id')[
            "balance"]


def get_trend_coordinator_flow(bank_account_pd):
    trend_coordinator_expense = db.session.query(Expense.fk_trend_coordinator_id, Expense.fk_bank_account_id
                                                 , func.sum(Expense.amount).label("expense_amount")) \
        .group_by(Expense.fk_trend_coordinator_id, Expense.fk_bank_account_id) \
        .order_by(Expense.fk_bank_account_id)
    trend_coordinator_expense_df = pd.read_sql(trend_coordinator_expense.statement, db.engine)
    trend_coordinator_expense_df[['fk_trend_coordinator_id', 'fk_bank_account_id']] = trend_coordinator_expense_df[
        ['fk_trend_coordinator_id', 'fk_bank_account_id']].apply(pd.to_numeric, errors='coerce')

    trend_coordinator_income = db.session.query(Income.fk_trend_coordinator_id, Income.fk_bank_account_id
                                                , func.sum(Expense.amount).label("income_amount")) \
        .group_by(Income.fk_trend_coordinator_id, Income.fk_bank_account_id) \
        .order_by(Income.fk_bank_account_id)
    trend_coordinator_income_df = pd.read_sql(trend_coordinator_income.statement, db.engine)
    trend_coordinator_income_df[['fk_trend_coordinator_id', 'fk_bank_account_id']] = trend_coordinator_income_df[
        ['fk_trend_coordinator_id', 'fk_bank_account_id']].apply(pd.to_numeric, errors='coerce')

    trend_coordinator_df = trend_coordinator_expense_df.merge(trend_coordinator_income_df, how='inner',
                                                              on=['fk_trend_coordinator_id', 'fk_bank_account_id'])
    trend_coordinator_df['trend_coordinator_balance'] = trend_coordinator_df['income_amount'] - trend_coordinator_df[
        'expense_amount']
    trend_coordinator_df = trend_coordinator_df[trend_coordinator_df['trend_coordinator_balance'] > 0]
    trend_coordinator_df = trend_coordinator_df[['fk_bank_account_id', 'trend_coordinator_balance']]
    trend_coordinator_df = trend_coordinator_df.groupby('fk_bank_account_id') \
        .agg(trend_coordinator_balance=('trend_coordinator_balance', 'sum')).reset_index()

    bank_account_pd = \
        bank_account_pd.merge(trend_coordinator_df, how='left', left_on='id', right_on='fk_bank_account_id')
    return bank_account_pd['trend_coordinator_balance']


def get_bank_account_total_loans(bank_account_pd):
    loans = db.session.query(Loan.fk_account_id, func.sum(Loan.total_amount).label("loan")).group_by(
        Loan.fk_account_id).order_by(Loan.fk_account_id)
    loans_pd = pd.read_sql(loans.statement, db.engine)
    bank_account_pd['id'], loans_pd['fk_account_id'] = pd.to_numeric(bank_account_pd['id']), pd.to_numeric(
        loans_pd['fk_account_id'])

    return bank_account_pd.merge(loans_pd, how='left', right_on='fk_account_id',
                                 left_on='id')["loan"]


def get_bank_accounts():
    accounts = []
    bank_accounts_df = db.session.query(BankAccount.id, BankAccount.account_number,
                                        Institution.name.label("institution_name"), BankAccount.line_of_credit) \
        .outerjoin(Institution).order_by(BankAccount.id)
    bank_account_pd = pd.read_sql(bank_accounts_df.statement, db.engine)

    bank_account_pd["balance"] = get_bank_account_balances(bank_account_pd)
    bank_account_pd["commitment"] = get_bank_account_commitments(bank_account_pd)
    bank_account_pd["cash_commitment"] = get_bank_account_commitments(bank_account_pd, cash=True)
    bank_account_pd["monthly_commitment"] = get_bank_account_monthly_commitments(bank_account_pd)
    bank_account_pd["flow"] = bank_account_pd["balance"] - bank_account_pd["commitment"]
    bank_account_pd["monthly_flow"] = bank_account_pd["balance"] - bank_account_pd["monthly_commitment"]
    bank_account_pd["trend_coordinator_flow"] = bank_account_pd["balance"] - get_trend_coordinator_flow(bank_account_pd)
    bank_account_pd["cash"] = bank_account_pd["balance"] - bank_account_pd["cash_commitment"]
    bank_account_pd["loan"] = get_bank_account_total_loans(bank_account_pd)
    bank_account_pd["institution_name"] = bank_account_pd["institution_name"].fillna("")
    bank_account_pd = bank_account_pd.fillna(0)

    headers = list(bank_account_pd.columns.values)
    for _, row in bank_account_pd.iterrows():
        account = {}
        for header in headers:
            if header != "cash_commitment" and header != "monthly_commitment":
                account[header] = row[header]
        accounts.append(account)
    return accounts


class BankAccountAPI(Resource):
    @login_required()
    def get(self, bank_account_id=None):
        if bank_account_id:
            results = BankAccount.read(many=False, id=bank_account_id)
        elif "verbose" in request.args and request.args.get('verbose') == "true":
            results = get_bank_accounts()
        else:
            results = BankAccount.read()
        return jsonify(results)

    @login_required()
    def post(self):
        bank_json = request.get_json()
        return jsonify(BankAccount.create(bank_json))

    @login_required()
    def put(self, bank_account_id):
        bank_json = request.get_json()
        return jsonify(BankAccount.update(bank_json, id=bank_account_id))

    @login_required()
    def delete(self, bank_account_id):
        return jsonify(BankAccount.delete(id=bank_account_id))
