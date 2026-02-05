import datetime, os, shutil
import pandas as pd
from core.utils import create_dir

from school_manager.db import db
from school_manager.models.crud_mixin import BaseMixin

from school_manager.modules.print.print_msv import PrintIncomeMSV

from school_manager.constants.constants_lists import UPLOAD_SOURCES
from datetime import datetime

DIR_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_EXPORT_PATH = os.path.join(DIR_PATH, 'assets/income/exports')


class Income(BaseMixin, db.Base):
    __tablename__ = "income"
    __classnameheb__ = "הכנסה"
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    deposit_date = db.Column(db.DateTime, nullable=False)
    # The date the payment is for , for example 1.6.2020
    for_month = db.Column(db.DateTime, nullable=False)
    # The date the payment is transmitted , for example 1.6.2020
    transmission_date = db.Column(db.DateTime, nullable=True)
    # The date that the payment created
    created_date = db.Column(db.DateTime, default=datetime.now)

    printing_date = db.Column(db.DateTime, nullable=True)
    # Payment Amount
    amount = db.Column(db.Float, nullable=False)
    # Attribution - who is related to this income - student / trend coordinator / institution etc...
    # attribution = db.Column(db.String(45))
    # The id of the related object itself, for example the id of a specific student
    # attribution_id = db.Column(db.Integer)
    payment_reason = db.Column(db.String(45))
    # Chain bank account id
    fk_bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_account.id'))
    fk_income_source_id = db.Column(db.Integer, db.ForeignKey('income_source.id'), nullable=False)
    fk_trend_coordinator_id = db.Column(db.Integer, db.ForeignKey('trend_coordinator.id'))
    # The Institution ID which received the payment
    fk_institution_id = db.Column(db.Integer, db.ForeignKey('institution.id'))
    # The Branch ID which received the payment
    fk_branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'))
    fk_current_account_id = db.Column(db.Integer, db.ForeignKey('current_account.id'))
    fk_donator_id = db.Column(db.Integer, db.ForeignKey('donator.id'))
    fk_periodic_reception_id = db.Column(db.Integer, db.ForeignKey('periodic_reception.id'))
    # attributions fks
    fk_student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    fk_course_enrollment_id = db.Column(db.Integer, db.ForeignKey('course_enrollment.id'))
    fk_employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    fk_supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
    fk_msv_file_id = db.Column(db.Integer, db.ForeignKey('msv_file.id'))

    # Payment method , cash \ check \ MASAV etc..
    method = db.Column(db.String(45), nullable=False)
    # The status of the payment - cancelled, draft, delivered etc..
    payment_status = db.Column(db.String(45), default='טיוטה')

    fund_raiser = db.Column(db.String(45))
    internal_system_action = db.Column(db.Boolean, default=False)
    is_printable = db.Column(db.Boolean, default=False)

    # Allotment
    eligibility_method = db.Column(db.String(45))
    eligibility_level = db.Column(db.Integer, default=0)
    eligibility_min = db.Column(db.Integer)
    excellence_fund_allotment = db.Column(db.Integer)
    aid_fund_allotment = db.Column(db.Integer)
    test_fund_allotment = db.Column(db.Integer)
    teaching_fund_allotment = db.Column(db.Integer)

    payment_classification = db.Column(db.String(45))

    data_source = db.Column(db.String(20), default=UPLOAD_SOURCES[0])
    data_upload_date = db.Column(db.DateTime, default=datetime.now)

    # Clearing
    # clearing_company = db.Column(db.String(45))
    # clearing_description = db.Column(db.String(250))
    # clearing_comments = db.Column(db.String(250))
    # clearing_transaction_number = db.Column(db.Integer)

    # Relationships
    income_source = db.relationship('IncomeSource', uselist=False)

    # Unique Constraints
    __table_args__ = (db.UniqueConstraint('for_month', 'fk_trend_coordinator_id', 'fk_institution_id',
                                          'fk_branch_id', 'fk_student_id', 'fk_employee_id', 'fk_supplier_id'
                                          , name='_student_income_uc'),)

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                {i: self.__dict__[i] for i in self.__dict__ if i != "_sa_instance_state"})


    @classmethod
    def export_draft(cls,expense_ids=[]):
        main_dir_name = f"Payments {datetime.datetime.today().strftime('%Y-%m-%d--%H-%M')}"
        main_dir_path = os.path.join(DEFAULT_EXPORT_PATH, main_dir_name)
        create_dir(main_dir_path)

        checks = PrintIncomeMSV(expense_ids=expense_ids,export_path=main_dir_path)
        checks.run()

        msvs = PrintIncomeMSV(expense_ids=expense_ids,export_path=main_dir_path)
        msvs.run()

        shutil.make_archive(main_dir_path, 'zip', root_dir=DEFAULT_EXPORT_PATH,base_dir=main_dir_name)
        with open(f"{main_dir_path}.zip", 'rb') as f:
            data = f.readlines()

        return data, f"{main_dir_name}.zip"


