from school_manager.db import db
from school_manager.models.crud_mixin import BaseMixin

from school_manager.constants.constants_lists import UPLOAD_SOURCES
from datetime import datetime

class ClearingCredit(BaseMixin, db.Base):
    __tablename__ = "clearing_credit"
    __classnameheb__ = "סליקת אשראי"
    # Columns
    id = db.Column(db.Integer, primary_key=True)

    # Clearing
    clearing_company = db.Column(db.String(45))
    clearing_description = db.Column(db.String(250))
    clearing_comments = db.Column(db.String(250))
    clearing_transaction_number = db.Column(db.Integer)

    source_coin = db.Column(db.Boolean,  nullable=False)
    original_amount = db.Column(db.Float,  nullable=False)
    fee_amount = db.Column(db.Float,  nullable=False)
    confirmation_number = db.Column(db.Float, nullable=False)
    validation_raw_confirmation_number = db.Column(db.Float, nullable=False)
    voucher_number = db.Column(db.Float, nullable=False)
    transaction_date = db.Column(db.DateTime, nullable=False)
    clearing_date = db.Column(db.DateTime, nullable=False)
    credit_four_digits = db.Column(db.Float, nullable=False)
    conversion_factor = db.Column(db.Float, nullable=False)
    credit_validity = db.Column(db.String(4), nullable=False)
    credit_brand = db.Column(db.String(20), nullable=False)
    terminal_number = db.Column(db.Float, nullable=False)
    platform_fee = db.Column(db.Float, nullable=False)

    data_source = db.Column(db.String(20), default=UPLOAD_SOURCES[0])
    data_upload_date = db.Column(db.DateTime, default=datetime.now)

    fk_platform_id = db.Column(db.Integer, db.ForeignKey('clearing_platform.id'))
    fk_income_id = db.Column(db.Integer, db.ForeignKey('income.id'))

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                {i: self.__dict__[i] for i in self.__dict__ if i != "_sa_instance_state"})