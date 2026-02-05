import os.path
import os
import pandas as pd
from datetime import datetime
from os import path

from core import utils
from school_manager.modules.payment_check.payment_check_generator import PaymentCheckGenerator


from sqlalchemy import and_
from sqlalchemy.sql import func
from school_manager.db import db

from school_manager.models.bank_account import BankAccount
from school_manager.models.institution import Institution

from school_manager.models.student import Student
from school_manager.models.employee import Employee
from school_manager.models.supplier import Supplier

from school_manager.constants.constants_lists import EXPENSE_PAYMENT_METHODS, EXPENSE_PAYMENT_STATUS

DIR_PATH = path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
DEFAULT_EXPORT_PATH = path.join(DIR_PATH, 'assets/expense/exports')

MAIN_FOLDER_NAME = "שיקים"
CHECK_PAYMENT_METHOD = EXPENSE_PAYMENT_METHODS[0]
DRAFT_PAYMENT_STATUS = EXPENSE_PAYMENT_STATUS[0]
PRINTED_PAYMENT_STATUS = EXPENSE_PAYMENT_STATUS[1]


class PrintExpenseCheck:

    def __init__(self, expense_ids=[], export_path=''):
        current_time = datetime.now().strftime('%Y-%m-%d--%H-%M')
        self.expense_ids = tuple(expense_ids)
        self.export_path = export_path if export_path else path.join(DEFAULT_EXPORT_PATH, current_time)
        self.check_data = None
        self.bank_account_check_numbers = {}
        self.institution_checks = {}
        self.create_check_error = []
        self.print_check_error = []
        self.merge_indexing = {}

        self.printed_check = 0
        self.printed_pdf = 0

        # self.set_check_data()

    def set_check_data(self):
        from school_manager.models.expense import Expense
        if self.expense_ids:
            filter_query = and_(Expense.payment_method == CHECK_PAYMENT_METHOD,
                                Expense.payment_status == DRAFT_PAYMENT_STATUS,
                                Expense.is_printable,
                                Expense.id.in_(self.expense_ids))
        else:
            filter_query = and_(Expense.payment_method == CHECK_PAYMENT_METHOD,
                                Expense.payment_status == DRAFT_PAYMENT_STATUS,
                                Expense.is_printable)

        check_query = db.session.query(Expense.id, Expense.fk_institution_id.label("institution_id"), Expense.amount,
                                       Expense.for_month, Expense.transmission_date, Expense.check_number,
                                       Expense.fk_branch_id, Expense.fk_student_id, Expense.fk_employee_id,
                                       Expense.fk_supplier_id,Expense.merged_printing_number,
                                       BankAccount.account_number, BankAccount.prev_account_number,
                                       BankAccount.phone_number.label("bank_phone_number"),
                                       BankAccount.branch_number, BankAccount.bank_number,
                                       BankAccount.branch_name, BankAccount.city.label('bank_city'),
                                       BankAccount.street, BankAccount.street_number,
                                       BankAccount.current_check_number, BankAccount.last_check_number,
                                       BankAccount.signature_image,
                                       Institution.city.label("institution_city"), Institution.zip_code,
                                       Institution.phone_number.label("institution_phone_number"),
                                       Institution.name.label("institution_name"),
                                       Institution.identity.label("institution_identity"),
                                       func.concat(Student.first_name, " ", Student.last_name).label("student_name"),
                                       func.concat(Employee.first_name, " ", Employee.last_name).label("employee_name"),
                                       Supplier.name.label("supplier_name")) \
            .join(Institution, Institution.id == Expense.fk_institution_id) \
            .join(BankAccount, BankAccount.id == Expense.fk_bank_account_id) \
            .join(Student, Student.id == Expense.fk_student_id, isouter=True) \
            .join(Employee, Employee.id == Expense.fk_employee_id, isouter=True) \
            .join(Supplier, Supplier.id == Expense.fk_supplier_id, isouter=True) \
            .filter(filter_query) \
            .order_by(Expense.fk_institution_id)

        check_df = pd.read_sql(check_query.statement, db.engine)
        check_df['transmission_date'] = check_df['transmission_date'].fillna(datetime(1990, 1, 1))
        check_df['for_month'] = check_df['for_month'].fillna(datetime(1990, 1, 1))
        # create single attribution
        check_df['full_name'] = check_df['student_name'].fillna(check_df['employee_name']).fillna(
            check_df['supplier_name'])
        self.check_data = check_df.fillna(0)

    def merge_check_data(self):
        merged_data = pd.DataFrame(columns=self.check_data.columns)

        self.check_data['merged_printing_number'] = self.check_data['merged_printing_number'].fillna(self.check_data['id'])
        grouped_msv_data = self.check_data.groupby(['merged_printing_number'], as_index=False)
        for group_index, group_df in grouped_msv_data:
            self.merge_indexing[group_index] = group_df['id'].tolist()
            amount = group_df['amount'].sum()
            group_df = group_df.head(1).reset_index()
            group_df['amount'] = amount
            merged_data = pd.concat([merged_data,group_df], axis=0)

        self.check_data = merged_data

    def create_check_per_institution(self):
        institution_check_df = self.check_data.groupby(['institution_id', 'institution_name', 'institution_identity']
                                                       , as_index=False)
        self.bank_account_check_numbers = self.get_bank_account_check_numbers()
        for institution_fields, institution_data in institution_check_df:
            institution_id_name = f"{institution_fields[1]}-{institution_fields[2]}"
            self.institution_checks[institution_id_name] = dict(checks=[], records=[])

            for index, expense_row in institution_data.iterrows():
                try:
                    current_check_number = self.bank_account_check_numbers[expense_row['account_number']][
                        'current_check_number']
                    last_check_number = self.bank_account_check_numbers[expense_row['account_number']][
                        'last_check_number']

                    if current_check_number > last_check_number:
                        raise Exception('Account reached last check number')
                    check_num = current_check_number
                    branch_barcode = f"{expense_row['branch_number']}{'0' * (5 - len(str(expense_row['branch_number'])))}"
                    barcode = f"{check_num} {expense_row['bank_number']} {branch_barcode} {expense_row['account_number']}"
                    # check_header = self.create_check_header(expense_row, barcode)
                    # check_body = self.create_check_body(expense_row)
                    # check_footer = self.create_check_footer(expense_row, barcode)
                    # check_appendix = self.create_check_appendix(expense_row, check_num)

                    self.institution_checks[institution_id_name]['checks'].append(PaymentCheckGenerator(pd.DataFrame(expense_row)).generate())
                    self.institution_checks[institution_id_name]['records'].append((expense_row, check_num))
                    self.bank_account_check_numbers[expense_row['account_number']]['current_check_number'] += 1
                except Exception as e:
                    self.create_check_error.append(dict(error=str(e), data=expense_row))

    def get_bank_account_check_numbers(self):
        bank_account_df = self.check_data[['account_number', 'current_check_number', 'last_check_number']]
        bank_account_df = bank_account_df.groupby('account_number').agg(
            current_check_number=pd.NamedAgg(column="current_check_number", aggfunc="max"),
            last_check_number=pd.NamedAgg(column="last_check_number", aggfunc="max")
        )
        return bank_account_df.to_dict('index')

    def create_check_header(self, expense_row, barcode):
        return CheckHeader(account_num=str(expense_row["account_number"]),
                           previous_account_num=str(expense_row["prev_account_number"]),
                           institution=expense_row["institution_name"][::-1],
                           association=expense_row["institution_identity"],
                           phone_num=expense_row["institution_phone_number"],
                           bank_branch_num=str(expense_row["branch_number"]),
                           bank_branch_name=expense_row['branch_name'][::-1],
                           bank_address=f"{expense_row['bank_city'][::-1]} {expense_row['street_number']} {expense_row['street'][::-1]}",
                           bank_phone_num=expense_row["bank_phone_number"], barcode=barcode,
                           mail=f"{expense_row['institution_city'][::-1]} {expense_row['zip_code']}")

    def create_check_body(self, expense_row):
        from num2words import num2words
        amount_string = u'{}'.format(num2words(expense_row["amount"], lang='heb'))[::-1]
        return CheckBody(addressee_name=expense_row["full_name"][::-1], amount=str(expense_row["amount"]),
                         amount_string=amount_string)

    def create_check_footer(self, expense_row, barcode):
        return CheckFooter(signature_file_name=expense_row["signature_image"],
                           due_date=expense_row["transmission_date"].strftime('%d/%m/%Y'), barcode=barcode)

    def create_check_appendix(self, expense_row, check_num):
        return CheckAppendix(addressee_name=expense_row["full_name"][::-1],
                             amount=str(expense_row["amount"]), due_date=expense_row["transmission_date"].strftime('%d/%m/%Y'),
                             check_num=str(check_num), month=expense_row["for_month"].strftime('%m/%Y'))

    def update_bank_account_check_number(self):
        for account_number, account_data in self.bank_account_check_numbers.items():
            BankAccount.update({'current_check_number':account_data['current_check_number']},
                               account_number=account_number)

    def update_printed_checks(self, records, printing_date):
        from school_manager.models.expense import Expense
        for record in records:
            record_data, check_num = record[0], record[1]
            for expense_id in self.merge_indexing.get(record_data.get('merged_printing_number'),[]):
                expense = Expense.update({'payment_status': PRINTED_PAYMENT_STATUS, 'check_number': check_num,
                                          'check_printing_date': printing_date},
                                         id=expense_id)


    def create_log(self):
        file_name = 'check_error.log' if self.create_check_error else 'check_success.log'
        with open(path.join(self.export_path, file_name), 'a', encoding="utf-8") as f:
            for record in self.create_check_error:
                error, data = record.get('error'), record.get('data')
                f.write(f'{error} \n {str(data)}')
            f.write(f'{self.printed_check} checks and {self.printed_pdf} pdf files were created.\n')

    def run(self):
        self.set_check_data()
        self.merge_check_data()
        self.create_check_per_institution()

        for institution, institution_data in self.institution_checks.items():
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
            institution_dir_path = path.join(self.export_path, institution)
            utils.create_dir(institution_dir_path)

            PaymentCheckGenerator(institution_data['checks'], output_path=os.path.join(institution_dir_path, institution.split("-")[1] + ".pdf")).generate()
            # check_file = PaymentCheckFile(checks=institution_data['checks'], output_path=institution_dir_path,
            #                               file_name=institution.split("-")[1])
            # check_file.dump()
            self.printed_check += len(institution_data['checks'])
            self.printed_pdf += len(institution_data['checks']) // 4
            if len(institution_data['checks']) % 4:
                self.printed_pdf += 1
            self.update_printed_checks(institution_data['records'], current_time)
        self.update_bank_account_check_number()
        self.create_log()
