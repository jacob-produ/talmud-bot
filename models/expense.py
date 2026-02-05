import os,shutil
import pandas as pd

from core.utils import create_dir

from school_manager.models.crud_mixin import BaseMixin
from school_manager.models.parameter import Parameter

from school_manager.db import db

from school_manager.modules.print.print_check import PrintExpenseCheck
from school_manager.modules.print.print_msv import PrintExpenseMSV


from school_manager.constants.constants_lists import UPLOAD_SOURCES
from datetime import datetime

# get school_manger path
DIR_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_EXPORT_PATH = os.path.join(DIR_PATH,'assets/expense/exports')


TRIGGER_NAME = 'expense_update_up_date'

UPDATE_TRIGGER_QUERY = f'''
            CREATE TRIGGER {TRIGGER_NAME} BEFORE UPDATE ON expense
            FOR EACH ROW
            BEGIN
                SET NEW.update_date = CONVERT_TZ (NOW(), 'SYSTEM','+03:00');
            END
        '''

class Expense(BaseMixin, db.Base):
    __tablename__ = "expense"
    __classnameheb__ = "הוצאה"
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    # The amount of expense
    amount = db.Column(db.Float, nullable=False)
    # The last time this line was modified
    update_date = db.Column(db.DateTime, default=datetime.now)
    # The date that the payment is for
    for_month = db.Column(db.DateTime)
    # The date that the payment created
    created_date = db.Column(db.DateTime ,default=datetime.now)
    # Attribution - who is related to this income - student / employee..
    # attribution = db.Column(db.String(45))
    # The id of the related object itself, for example the id of a specific student
    # attribution_id = db.Column(db.Integer)
    # For example - check, masav, cash etc..
    payment_method = db.Column(db.String(45))
    # The status of the payment - cancelled, draft, delivered etc..
    payment_status = db.Column(db.String(45), default='טיוטה')
    # The actual payment date - execution date
    actual_payment_date = db.Column(db.DateTime)
    # This is the serial number thats MASAV system gave our MSV file Its not clear yet how we can extract the msv number
    masav_number = db.Column(db.Integer)
    check_number = db.Column(db.Integer)
    merged_printing_number = db.Column(db.Integer)
    # Check due date (Pirahon in hebrew)
    transmission_date = db.Column(db.DateTime)
    # Check print date can help us show which checks were printed on a specific date
    check_printing_date = db.Column(db.DateTime)
    # In case of scholarship expense
    scholarship_type = db.Column(db.String(45))
    scholarship_method = db.Column(db.String(45))
    check_pdf = db.Column(db.String(150))
    is_printable = db.Column(db.Boolean,default=False)
    internal_system_action = db.Column(db.Boolean,default=False)
    comments = db.Column(db.String(250))

    payment_classification = db.Column(db.String(45))

    data_source = db.Column(db.String(20), default=UPLOAD_SOURCES[0])
    data_upload_date = db.Column(db.DateTime, default=datetime.now)

    # Can indicate the source of income that will cover this expsense
    fk_income_source_id = db.Column(db.Integer, db.ForeignKey('income_source.id'))
    fk_trend_coordinator_id = db.Column(db.Integer, db.ForeignKey('trend_coordinator.id'))
    fk_institution_id = db.Column(db.Integer, db.ForeignKey('institution.id'))
    fk_branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'))
    fk_bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_account.id'))
    fk_general_bank_account_id = db.Column(db.Integer, db.ForeignKey('general_bank_account.id'))
    fk_current_account_id = db.Column(db.Integer, db.ForeignKey('current_account.id'))
    fk_msv_file_id = db.Column(db.Integer, db.ForeignKey('msv_file.id'))
    # attributions fks
    fk_student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    fk_course_enrollment_id = db.Column(db.Integer, db.ForeignKey('course_enrollment.id'))
    fk_employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    fk_supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                {i: self.__dict__[i] for i in self.__dict__ if i != "_sa_instance_state"})



    @classmethod
    def export_draft(cls, expense_ids=[]):
        main_dir_name = f"Payments {datetime.today().strftime('%Y-%m-%d--%H-%M')}"
        main_dir_path = os.path.join(DEFAULT_EXPORT_PATH, main_dir_name)
        create_dir(main_dir_path)

        checks = PrintExpenseCheck(expense_ids=expense_ids,export_path=main_dir_path)
        checks.run()

        msvs = PrintExpenseMSV(expense_ids=expense_ids,export_path=main_dir_path)
        msvs.run()

        shutil.make_archive(main_dir_path, 'zip', root_dir=DEFAULT_EXPORT_PATH,base_dir=main_dir_name)
        with open(f"{main_dir_path}.zip", 'rb') as f:
            data = f.readlines()

        return data, f"{main_dir_name}.zip"

    @classmethod
    def get_merge_expense_by_id(cls, expense_ids=(), fields=[]):
        db_fields = [getattr(cls, field) for field in fields]
        query = db.session.query(*db_fields).filter(Expense.id.in_(expense_ids))
        main_df = pd.read_sql(query.statement, db.engine)
        main_df['transmission_date'] = main_df['transmission_date'].fillna(datetime.datetime(1900,1,1))
        return main_df.fillna(-1)

    @classmethod
    def update_merge_number(cls,merged_printing_number, expense_ids=[]):
        if not expense_ids:
            return
        for expense_id in expense_ids:
            Expense.update(dict(merged_printing_number=merged_printing_number), id=expense_id)

    @classmethod
    def merge_payment(cls, expense_ids=[]):
        expense_ids = tuple(expense_ids)
        expense_merge_last_value = Parameter.read_all_parameters().get('expense_merge_last_value',0)
        if not expense_ids:
            raise NotImplementedError()
        fields = ['id', 'merged_printing_number', 'payment_method','transmission_date','fk_bank_account_id',
                  'fk_general_bank_account_id', 'fk_student_id','fk_employee_id','fk_supplier_id']
        group_by_fields = list(set(fields) - set(['id','merged_printing_number']))
        unmerge_expenses = []
        main_df = cls.get_merge_expense_by_id(expense_ids, fields)
        grouped_by_expenses = main_df.groupby(group_by_fields)
        for group_index, group_df in grouped_by_expenses:
            if group_df.shape[0] == 1:
                unmerge_expenses.append(int(group_df.reset_index().at[0, 'id']))
                continue
            current_merge_number = group_df['merged_printing_number'].max()
            if current_merge_number > 0:
                merge_number = current_merge_number
            else:
                merge_number = expense_merge_last_value
                expense_merge_last_value += 1
            group_df = group_df[group_df['merged_printing_number'] != merge_number]
            cls.update_merge_number(merge_number, group_df['id'].tolist())
        update = Parameter.update(dict(value=str(expense_merge_last_value)), name='expense_merge_last_value')
        print(update)
        return unmerge_expenses

    @classmethod
    def split_payment(cls, expense_ids=[]):
        for expense_id in expense_ids:
            Expense.update(dict(merged_printing_number=None), id=expense_id)


if __name__ == '__main__':
    # Expense.export_draft_to_msv()
    x = Expense.get_msv_df(draft=False)
    x.head()