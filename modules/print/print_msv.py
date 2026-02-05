import pandas as pd, math
from datetime import datetime
from os import path
import numpy as np
from core import utils

from school_manager.modules.masav import masav
from school_manager.modules.masav import masav_income

from sqlalchemy import and_
from sqlalchemy.sql import func
from school_manager.db import db

from school_manager.models.general_bank_account import GeneralBankAccount
from school_manager.models.institution import Institution
from school_manager.models.msv_file import MSVFile
from school_manager.models.course_enrollment import CourseEnrollment

from school_manager.models.student import Student
from school_manager.models.employee import Employee
from school_manager.models.supplier import Supplier

from school_manager.constants.constants_lists import EXPENSE_PAYMENT_METHODS, EXPENSE_PAYMENT_STATUS, \
    INCOME_PAYMENT_METHODS, INCOME_PAYMENT_STATUS
from school_manager.constants.constants_lists import GENERAL_BANK_ACCOUNT_STATUS, EXPENSE_PAYMENT_CLASSIFICATION
from school_manager.constants import constants

DIR_PATH = path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
DEFAULT_EXPENSE_EXPORT_PATH = path.join(DIR_PATH, 'assets/expense/exports')
DEFAULT_INCOME_EXPORT_PATH = path.join(DIR_PATH, 'assets/income/exports')

MAIN_FOLDER_NAME = "שיקים"

EXPENSE_MSV_PAYMENT_METHOD = EXPENSE_PAYMENT_METHODS[1]
EXPENSE_DRAFT_PAYMENT_STATUS = EXPENSE_PAYMENT_STATUS[0]
EXPENSE_PRINTED_PAYMENT_STATUS = EXPENSE_PAYMENT_STATUS[1]


class PrintMSV:
    def __init__(self, expense_ids=[], export_path=''):
        current_time = datetime.now().strftime('%Y-%m-%d--%H-%M')
        self.expense_ids = tuple(expense_ids)
        self.export_path = export_path
        self.msv_data = None
        self.institution_msv = {}
        self.create_msv_error = []

        self.merge_indexing = {}

        self.printed_msv = 0
        self.printed_transactions = 0

    def get_general_bank_account_data(self):
        general_ba_query = db.session.query(GeneralBankAccount.fk_student_id, GeneralBankAccount.fk_supplier_id,
                                            GeneralBankAccount.fk_employee_id,
                                            GeneralBankAccount.bank_number, GeneralBankAccount.account_number,
                                            GeneralBankAccount.branch_number, GeneralBankAccount.status)

        general_ba_df = pd.read_sql(general_ba_query.statement, db.engine)
        general_ba_df['fk_student_id'] = general_ba_df['fk_student_id'].fillna('')
        general_ba_df['fk_supplier_id'] = general_ba_df['fk_supplier_id'].fillna('')
        general_ba_df['fk_employee_id'] = general_ba_df['fk_employee_id'].fillna('')
        general_ba_groups = general_ba_df.groupby(['fk_student_id', 'fk_supplier_id', 'fk_employee_id'],
                                                  as_index=False)
        general_ba_last_account = pd.DataFrame(columns=general_ba_df.columns)

        for group_name, group_df in general_ba_groups:
            bank_account = group_df[group_df['status'] == GENERAL_BANK_ACCOUNT_STATUS[0]]
            if bank_account.shape[0] > 0:
                bank_account = bank_account.iloc[[-1]]
            elif group_df[group_df['status'] == GENERAL_BANK_ACCOUNT_STATUS[1]].shape[0] > 0:
                bank_account = group_df[group_df['status'] == GENERAL_BANK_ACCOUNT_STATUS[1]].iloc[[-1]]
            else:
                bank_account = group_df[group_df['status'] != GENERAL_BANK_ACCOUNT_STATUS[2]].iloc[[-1]]
            general_ba_last_account = pd.concat([general_ba_last_account, bank_account], axis=0)
        general_ba_last_account['fk_student_id'] = general_ba_last_account['fk_student_id'].replace({'': np.nan})
        general_ba_last_account['fk_supplier_id'] = general_ba_last_account['fk_supplier_id'].replace({'': np.nan})
        general_ba_last_account['fk_employee_id'] = general_ba_last_account['fk_employee_id'].replace({'': np.nan})
        return general_ba_last_account

    def get_attribution_type(self, row):
        if row.empty: return None
        if row['fk_student_id'] and not math.isnan(row['fk_student_id']):
            return 'student'
        elif row['fk_employee_id'] and not math.isnan(row['fk_employee_id']):
            return 'employee'
        elif row['fk_supplier_id'] and not math.isnan(row['fk_supplier_id']):
            return 'supplier'
        return 'without'

    def set_msv_data(self):
        raise NotImplementedError()

    def create_msv_per_institution(self):
        for index, expense_row in self.msv_data.iterrows():
            institution_id = f"{str(expense_row['institution_name'])}-{expense_row['institution_identity']}"

            if institution_id not in self.institution_msv:
                mh = masav.MSVHeader(institute_code=expense_row["msv_institute_code"],
                                     sending_institute_code=expense_row["msv_sending_institute_code"],
                                     institute_name=expense_row["institution_name"])

                self.institution_msv[institution_id] = {"mh": mh, "transactions": [], "records": []}
            else:
                mh = self.institution_msv[institution_id]["mh"]
            transaction = masav.MSVTransaction(mh, bank_code=expense_row["bank_number"],
                                               bank_branch_code=expense_row["branch_number"],
                                               bank_account_number=expense_row["account_number"],
                                               payee_tz=expense_row["identity"],
                                               payee_name=expense_row["full_name"],
                                               payment_amount=expense_row["amount"],
                                               payee_institution_identifier=expense_row["institution_identity"])
            self.institution_msv[institution_id]["transactions"].append(transaction)
            self.institution_msv[institution_id]["records"].append(expense_row)

    def get_payment_classification(self, attribution, attribution_id, fk_branch_id, for_month):
        if attribution == 'employee':
            return EXPENSE_PAYMENT_CLASSIFICATION[0]
        elif attribution == 'supplier':
            return EXPENSE_PAYMENT_CLASSIFICATION[1]

        student_courses = CourseEnrollment.read(many=True, id=attribution_id, fk_branch_id=fk_branch_id)
        for student_course in student_courses:
            start_date, end_date = student_course['start_date'], student_course['end_date']
            if end_date is None:
                return EXPENSE_PAYMENT_CLASSIFICATION[2]
            if datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S') > for_month:
                return EXPENSE_PAYMENT_CLASSIFICATION[2]
        return EXPENSE_PAYMENT_CLASSIFICATION[3]

    def update_printed_msv(self, records, printing_date, file_name):
        NotImplementedError()


    def create_log(self):
        file_name = 'msv_success.log'
        with open(path.join(self.export_path, file_name), 'a', encoding="utf-8") as f:
            f.write(
                f'{self.printed_transactions} transactions and {self.printed_transactions} msv files were created.\n')

    def run(self):
        NotImplementedError()


class PrintExpenseMSV(PrintMSV):

    def __init__(self, expense_ids=[], export_path=None):
        if not export_path:
            export_path = DEFAULT_EXPENSE_EXPORT_PATH
        super().__init__(expense_ids=expense_ids,export_path=export_path)


    def set_msv_data(self):
        from school_manager.models.expense import Expense
        general_bank_account_df = self.get_general_bank_account_data()
        if self.expense_ids:
            filter_query = and_(Expense.payment_method == EXPENSE_MSV_PAYMENT_METHOD,
                                Expense.payment_status == EXPENSE_DRAFT_PAYMENT_STATUS,
                                Expense.is_printable,
                                Expense.id.in_(self.expense_ids))
        else:
            filter_query = and_(Expense.payment_method == EXPENSE_MSV_PAYMENT_METHOD,
                                Expense.payment_status == EXPENSE_DRAFT_PAYMENT_STATUS,
                                Expense.is_printable)
        msv_query = db.session.query(Expense.id, Expense.fk_institution_id.label("institution_id"), Expense.amount,
                                     Expense.fk_branch_id, Expense.for_month,Expense.merged_printing_number,
                                     Expense.fk_student_id, Expense.fk_employee_id, Expense.fk_supplier_id,
                                     Institution.name.label("institution_name"),
                                     Institution.identity.label("institution_identity"),
                                     Institution.msv_institute_code, Institution.msv_sending_institute_code,
                                     func.concat(Student.first_name, " ", Student.last_name).label("student_name"),
                                     Student.identity.label('student_identity'),
                                     func.concat(Employee.first_name, " ", Employee.last_name).label("employee_name"),
                                     Employee.identity.label('employee_identity'),
                                     Supplier.name.label("supplier_name"),
                                     Supplier.identity.label('supplier_identity')
                                     ) \
            .join(Institution, Institution.id == Expense.fk_institution_id) \
            .join(Student, Student.id == Expense.fk_student_id, isouter=True) \
            .join(Employee, Employee.id == Expense.fk_employee_id, isouter=True) \
            .join(Supplier, Supplier.id == Expense.fk_supplier_id, isouter=True) \
            .filter(filter_query) \
            .order_by(Expense.fk_institution_id)

        msv_df = pd.read_sql(msv_query.statement, db.engine)
        msv_df[['fk_student_id', 'fk_supplier_id', 'fk_employee_id']] = \
            msv_df[['fk_student_id', 'fk_supplier_id', 'fk_employee_id']].apply(pd.to_numeric, errors='coerce', axis=1)
        msv_df['attribution'] = msv_df.apply(self.get_attribution_type, axis=1)
        msv_df['for_month'] = msv_df['for_month'].fillna(datetime(1990, 1, 1))
        # create single attribution
        msv_df['full_name'] = msv_df['student_name'].fillna(msv_df['employee_name']).fillna(
            msv_df['supplier_name'])
        msv_df['identity'] = pd.to_numeric(msv_df['student_identity'].fillna(msv_df['employee_identity']).fillna(
            msv_df['supplier_identity']), errors='coerce')
        msv_df = msv_df.merge(general_bank_account_df, on=['fk_student_id', 'fk_supplier_id', 'fk_employee_id'],
                              how='left')
        self.msv_data = msv_df.fillna(0)

    def merge_msv_data(self):
        merged_data = pd.DataFrame(columns=self.msv_data.columns)

        self.msv_data['merged_printing_number'] = self.msv_data['merged_printing_number'].fillna(self.msv_data['id'])
        grouped_msv_data = self.msv_data.groupby(['merged_printing_number'], as_index=False)
        for group_index, group_df in grouped_msv_data:
            self.merge_indexing[group_index] = group_df['id'].tolist()
            amount = group_df['amount'].sum()
            group_df = group_df.head(1).reset_index()
            group_df['amount'] = amount
            merged_data = pd.concat([merged_data,group_df], axis=0)

        self.msv_data = merged_data

    def update_printed_msv(self, records, printing_date, file_name):
        from school_manager.models.expense import Expense
        for record in records:
            payment_classification = self.get_payment_classification(record['attribution'],
                                                                     record['fk_student_id'],
                                                                     record['fk_branch_id'],
                                                                     record['for_month'])
            msv_file_result = MSVFile.create({'amount': record.get('amount', 0),
                                              'file_name': file_name, 'date': printing_date})
            print(msv_file_result)
            msv_file_id = msv_file_result[constants.STR_DATA].get('id')
            for expense_id in self.merge_indexing.get(record.get('merged_printing_number'),[]):
                update_record = Expense.update({'payment_status': EXPENSE_PRINTED_PAYMENT_STATUS, 'fk_msv_file_id': msv_file_id,
                                            'check_printing_date': printing_date,
                                            'payment_classification': payment_classification},
                                           id=expense_id)
            # print(update_record)

    def run(self):

        self.set_msv_data()
        self.merge_msv_data()
        self.create_msv_per_institution()
        for institution, msv in self.institution_msv.items():
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
            institution_dir_path = path.join(self.export_path, institution)
            utils.create_dir(institution_dir_path)

            mf = masav.MSVFile(msv["mh"], msv["transactions"], msv_path=institution_dir_path,
                               name=institution.split('-')[1])
            mf.dump()
            self.printed_msv += 1
            self.printed_transactions += len(msv["transactions"])
            self.update_printed_msv(msv["records"], current_time, mf.msv_name)

        self.create_log()


INCOME_MSV_PAYMENT_METHOD = INCOME_PAYMENT_METHODS[3]
INCOME_DRAFT_PAYMENT_STATUS = INCOME_PAYMENT_STATUS[0]
INCOME_PRINTED_PAYMENT_STATUS = INCOME_PAYMENT_STATUS[5]


class PrintIncomeMSV(PrintMSV):

    def __init__(self, expense_ids=[], export_path=None):
        if not export_path:
            export_path = DEFAULT_INCOME_EXPORT_PATH
        super().__init__(expense_ids=expense_ids, export_path=export_path)

    def set_msv_data(self):
        from school_manager.models.income import Income
        general_bank_account_df = self.get_general_bank_account_data()
        if self.expense_ids:
            filter_query = and_(Income.method == INCOME_MSV_PAYMENT_METHOD,
                                Income.payment_status == INCOME_DRAFT_PAYMENT_STATUS,
                                Income.is_printable,
                                Income.id.in_(self.expense_ids))
        else:
            filter_query = and_(Income.method == INCOME_MSV_PAYMENT_METHOD,
                                Income.payment_status == INCOME_DRAFT_PAYMENT_STATUS,
                                Income.is_printable)
        msv_query = db.session.query(Income.id, Income.fk_institution_id.label("institution_id"), Income.amount,
                                     Income.fk_branch_id, Income.for_month,
                                     Income.fk_student_id, Income.fk_employee_id, Income.fk_supplier_id,
                                     Institution.name.label("institution_name"),
                                     Institution.identity.label("institution_identity"),
                                     Institution.msv_institute_code, Institution.msv_sending_institute_code,
                                     func.concat(Student.first_name, " ", Student.last_name).label("student_name"),
                                     Student.identity.label('student_identity'),
                                     func.concat(Employee.first_name, " ", Employee.last_name).label("employee_name"),
                                     Employee.identity.label('employee_identity'),
                                     Supplier.name.label("supplier_name"),
                                     Supplier.identity.label('supplier_identity')
                                     ) \
            .join(Institution, Institution.id == Income.fk_institution_id) \
            .join(Student, Student.id == Income.fk_student_id, isouter=True) \
            .join(Employee, Employee.id == Income.fk_employee_id, isouter=True) \
            .join(Supplier, Supplier.id == Income.fk_supplier_id, isouter=True) \
            .filter(filter_query) \
            .order_by(Income.fk_institution_id)

        msv_df = pd.read_sql(msv_query.statement, db.engine)
        msv_df[['fk_student_id', 'fk_supplier_id', 'fk_employee_id']] = \
            msv_df[['fk_student_id', 'fk_supplier_id', 'fk_employee_id']].apply(pd.to_numeric, errors='coerce', axis=1)
        msv_df['attribution'] = msv_df.apply(self.get_attribution_type, axis=1)
        msv_df['for_month'] = msv_df['for_month'].fillna(datetime(1990, 1, 1))
        # create single attribution
        msv_df['full_name'] = msv_df['student_name'].fillna(msv_df['employee_name']).fillna(
            msv_df['supplier_name'])
        msv_df['identity'] = pd.to_numeric(msv_df['student_identity'].fillna(msv_df['employee_identity']).fillna(
            msv_df['supplier_identity']), errors='coerce')
        msv_df = msv_df.merge(general_bank_account_df, on=['fk_student_id', 'fk_supplier_id', 'fk_employee_id'],
                              how='left')
        self.msv_data = msv_df.fillna(0)

    def update_printed_msv(self, records, printing_date, file_name):
        from school_manager.models.income import Income
        for record in records:
            payment_classification = self.get_payment_classification(record['attribution'],
                                                                     record['fk_student_id'],
                                                                     record['fk_branch_id'],
                                                                     record['for_month'])
            msv_file_result = MSVFile.create({'amount': record.get('amount', 0),
                                              'file_name': file_name, 'date': printing_date})
            print(msv_file_result)
            msv_file_id = msv_file_result[constants.STR_DATA].get('id')
            update_record = Income.update({'payment_status': EXPENSE_PRINTED_PAYMENT_STATUS, 'fk_msv_file_id': msv_file_id,
                                        'printing_date': printing_date,
                                        'payment_classification': payment_classification},
                                       id=record.get('id'))
            print(update_record)


    def run(self):
        self.set_msv_data()
        self.create_msv_per_institution()
        for institution, msv in self.institution_msv.items():
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
            institution_dir_path = path.join(self.export_path, institution)
            utils.create_dir(institution_dir_path)

            mf = masav_income.MSVFile(msv["mh"], msv["transactions"], msv_path=institution_dir_path,
                                      name=institution.split('-')[1])
            mf.dump()
            self.printed_msv += 1
            self.printed_transactions += len(msv["transactions"])
            self.update_printed_msv(msv["records"], current_time, mf.msv_name)

        self.create_log()
