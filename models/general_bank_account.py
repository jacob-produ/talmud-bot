from school_manager.db import db
from school_manager.models.crud_mixin import BaseMixin
from school_manager.constants import constants_lists

from school_manager.constants.constants_lists import UPLOAD_SOURCES
from datetime import datetime

class GeneralBankAccount(BaseMixin, db.Base):
    __tablename__ = "general_bank_account"
    __classnameheb__ = "חשבונות בנק כללי"
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    bank_number = db.Column(db.Integer, nullable=False)
    branch_number = db.Column(db.Integer)
    account_number = db.Column(db.Integer, nullable=False)

    data_source = db.Column(db.String(20), default=UPLOAD_SOURCES[0])
    data_upload_date = db.Column(db.DateTime, default=datetime.now)


    # attributions fks
    fk_student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=True)
    fk_employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=True)
    fk_supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=True)
    fk_donator_id = db.Column(db.Integer, db.ForeignKey('donator.id'), nullable=True)

    status = db.Column(db.String(45), default=constants_lists.GENERAL_BANK_ACCOUNT_STATUS[0])

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                {i: self.__dict__[i] for i in self.__dict__ if i != "_sa_instance_state"})

    @classmethod
    def get_student_general_bank_account(cls, student_id):
        student_bank_accounts = cls.read(many=False, fk_student_id=student_id)
        if not student_bank_accounts:
            return {}
        secondary_bank_account, last_bank_account = None, None
        for bank_account in student_bank_accounts:
            # default bank account
            if bank_account.get('status') == constants_lists.GENERAL_BANK_ACCOUNT_STATUS[0]:
                return bank_account
            elif bank_account.get('status') == constants_lists.GENERAL_BANK_ACCOUNT_STATUS[1]:
                secondary_bank_account = bank_account
            last_bank_account = bank_account

        if secondary_bank_account: return secondary_bank_account
        return last_bank_account

    @classmethod
    def get_employee_general_bank_account(cls, employee_id):
        employee_bank_accounts = cls.read(many=False, fk_employee_id=employee_id)
        if not employee_bank_accounts:
            return {}
        secondary_bank_account, last_bank_account = None, None
        for bank_account in employee_bank_accounts:
            # default bank account
            if bank_account.get('status') == constants_lists.GENERAL_BANK_ACCOUNT_STATUS[0]:
                return bank_account
            elif bank_account.get('status') == constants_lists.GENERAL_BANK_ACCOUNT_STATUS[1]:
                secondary_bank_account = bank_account
            last_bank_account = bank_account

        if secondary_bank_account: return secondary_bank_account
        return last_bank_account

    @classmethod
    def get_supplier_general_bank_account(cls, supplier_id):
        supplier_bank_accounts = cls.read(many=False, fk_supplier_id=supplier_id)
        if not supplier_bank_accounts:
            return {}
        secondary_bank_account, last_bank_account = None, None
        for bank_account in supplier_bank_accounts:
            # default bank account
            if bank_account.get('status') == constants_lists.GENERAL_BANK_ACCOUNT_STATUS[0]:
                return bank_account
            elif bank_account.get('status') == constants_lists.GENERAL_BANK_ACCOUNT_STATUS[1]:
                secondary_bank_account = bank_account
            last_bank_account = bank_account

        if secondary_bank_account: return secondary_bank_account
        return last_bank_account
