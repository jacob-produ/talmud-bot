from school_manager.db import db
from school_manager.models.crud_mixin import BaseMixin

from school_manager.constants.constants_lists import UPLOAD_SOURCES
from datetime import datetime


class BankAccount(BaseMixin, db.Base):
    __tablename__ = "bank_account"
    __classnameheb__ = "חשבון בנק"
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    bank_number = db.Column(db.Integer, nullable=False)
    branch_name = db.Column(db.String(45))
    branch_number = db.Column(db.Integer, nullable=False)
    account_number = db.Column(db.Integer, nullable=False)
    prev_account_number = db.Column(db.Integer)
    city = db.Column(db.String(45))
    street = db.Column(db.String(45))
    street_number = db.Column(db.String(45))
    username = db.Column(db.String(45))
    password = db.Column(db.String(150))
    signature_image = db.Column(db.String(45))
    line_of_credit = db.Column(db.Integer)
    phone_number = db.Column(db.String(45), default="")
    first_check_number = db.Column(db.Integer, nullable=False, default=0)
    last_check_number = db.Column(db.Integer, nullable=False, default=100)
    current_check_number = db.Column(db.Integer, nullable=False, default=0)

    data_source = db.Column(db.String(20), default=UPLOAD_SOURCES[0])
    data_upload_date = db.Column(db.DateTime, default=datetime.now)

    fk_institution_id = db.Column(db.Integer, db.ForeignKey('institution.id'))

    __table_args__ = (
    db.UniqueConstraint('fk_institution_id', 'bank_number', 'account_number', name='_institution_symbol_uc'),)

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                {i: self.__dict__[i] for i in self.__dict__ if i != "_sa_instance_state"})

    @classmethod
    def get_bank_account_institution_id(cls, account_number):
        bank_account_record = cls.read(['id', 'fk_institution_id'], many=False, account_number=account_number)
        return bank_account_record.get('id'), bank_account_record.get('fk_institution_id')
