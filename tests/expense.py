import datetime
import random
from school_manager.models.expense import Expense
import os
from school_manager.models.student import Student
from school_manager.models.employee import Employee
from school_manager.models.supplier import Supplier
from school_manager.models.branch import Branch
from school_manager.constants import constants_lists

from school_manager.db import db, initialize_db
initialize_db.init_db()


def insert_model_expenses(model_class, attribution):
    branches = Branch.read()
    for obj in model_class.query.filter():
        insert_single_expense(attribution, obj.id, branches)


def insert_single_expense(attribution, attribution_id, branches):
    exp = Expense()
    exp.amount = random.randint(100, 10000)
    exp.for_month = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    exp.attribution = attribution
    exp.attribution_id = attribution_id
    exp.payment_method = random.choice(constants_lists.EXPENSE_PAYMENT_METHODS)
    exp.payment_status = random.choice(constants_lists.EXPENSE_PAYMENT_STATUS)

    if exp.payment_method == "מסב":
        exp.masav_number = random.randint(5000, 10000)
    elif exp.payment_method == "שיק":
        exp.check_number = random.randint(5000, 10000)
        exp.check_pdf = r'987312311-check_image.pdf'
        exp.check_date = datetime.date.today()
        exp.check_printing_date = datetime.date.today()

    if attribution == "student":
        exp.scholarship_type = random.choice(constants_lists.SCHOLARSHIP_TYPES)

    exp.actual_payment_date = datetime.date.today()
    exp.update_date = datetime.date.today()
    exp.execution_date = datetime.date.today()
    exp.fk_trend_coordinator_id = 1
    exp.fk_income_source_id = 1
    random_branch =  random.choice(branches)
    exp.fk_branch_id = random_branch
    exp.fk_institution_id = 1
    exp.fk_bank_account_id = 2
    exp.fk_msv_file_id = None
    db.session.add(exp)


if __name__ == "__main__":
    # # main()
    # print(datetime.datetime.now())
    # # insert_model_expenses(Student, "student")
    # # insert_model_expenses(Employee, "employee")
    # # insert_model_expenses(Supplier, "supplier")
    # insert_single_expense("supplier", 1,[1,2,3,4,5,6])
    # db.session.commit()
    # print(datetime.datetime.now())
    # print("Done")

    #test create msv file
    # Expense.export_draft_to_msv(path="E:\msv")
    Expense.export_draft(expense_ids=[])




