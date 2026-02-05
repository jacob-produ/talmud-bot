import re,time
import types
from core import date_utils
from school_manager.db import db
from school_manager.models.crud_mixin import BaseMixin
from school_manager.models.bank_account import BankAccount
from school_manager.modules.link_current_account.link_current_account import LinkCurrentAccount

from school_manager.constants.constants_lists import UPLOAD_SOURCES
from datetime import datetime

BANK_ACCOUNT_NUMBER_INDEX = 6
# Example - חשבון: 0075649823 | הדר יוסף ; Regex gets the account_number without the zeros at the beginning
BANK_ACCOUNT_REGEX_CSV = ":\s0*(\d+)\s\|"


class CurrentAccount(BaseMixin, db.Base):
    __tablename__ = "current_account"
    __classnameheb__ = "עובר ושב"
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    value_date = db.Column(db.DateTime)
    transaction_description = db.Column(db.String(512))
    transaction_amount = db.Column(db.Float, nullable=False)
    balance = db.Column(db.Float)
    # Proof \ Support - Asmachta; Sometimes it contains slash so it cannot be an int
    reference_number = db.Column(db.String(32), nullable=False)
    second_reference_number = db.Column(db.String(32), nullable=False, default='1')
    ca_file_id = db.Column(db.String(100), nullable=True)
    is_linked = db.Column(db.Boolean, default=False)
    comment = db.Column(db.String(40))

    bank_account_number = db.Column(db.Integer)
    branch_number = db.Column(db.Integer)
    bank_number = db.Column(db.Integer)
    front_image_link = db.Column(db.String(220))
    rear_image_link = db.Column(db.String(220))
    pdf_link = db.Column(db.String(220))
    check_number = db.Column(db.Integer)

    data_source = db.Column(db.String(20), default=UPLOAD_SOURCES[0])
    data_upload_date = db.Column(db.DateTime, default=datetime.now)

    fk_bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_account.id'),  nullable=False)
    fk_trend_coordinator_id = db.Column(db.Integer, db.ForeignKey('trend_coordinator.id'), nullable=True)


    # Relationships
    bank_account = db.relationship('BankAccount', uselist=True)
    expense = db.relationship('Expense', uselist=True)
    income = db.relationship('Income', uselist=True)

    # Unique Constraints
    __table_args__ = (db.UniqueConstraint('fk_bank_account_id', 'reference_number', 'second_reference_number',
                                          name='_bank_account_reference_uc'),)

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                {i: self.__dict__[i] for i in self.__dict__ if i != "_sa_instance_state"})

    @classmethod
    def get_csv_conversion_dict(cls):
        return {
            "date": (cls.get_date_str_as_date, "תאריך"),
            "value_date":(cls.get_date_str_as_date, "יום ערך"),
            "transaction_description": "תיאור התנועה",
            "transaction_amount": (cls.get_csv_str_as_number, "₪ זכות/חובה "),
            "balance": (cls.get_csv_str_as_number, "₪ יתרה "),
            "reference_number": "אסמכתה"
        }

    @classmethod
    def get_csv_str_as_number(cls, csv_cell):
        return float(csv_cell.replace(",", ""))

    @classmethod
    def get_date_str_as_date(cls, csv_cell):
        return date_utils.parse_date_from_str(csv_cell).isoformat()

    @classmethod
    def create_from_csv(cls, csv_reader, bank_account_id, fk_institution_id, file_name):
        current_account_rows = []
        file_id = f"{file_name} {int(time.time())}"
        for csv_row in csv_reader:
            if any(csv_row.values()):
                current_account_dict = {}
                # Convert csv row to db row
                for db_col, csv_col in cls.get_csv_conversion_dict().items():
                    if isinstance(csv_col, str):
                        current_account_dict[db_col] = csv_row[csv_col]
                    elif isinstance(csv_col, types.MethodType):
                        current_account_dict[db_col] = csv_col(csv_row)
                    elif isinstance(csv_col, tuple):
                        current_account_dict[db_col] = csv_col[0](csv_row[csv_col[1]])
                current_account_dict[CurrentAccount.col_name(CurrentAccount.fk_bank_account_id)] = bank_account_id
                current_account_dict["ca_file_id"] = file_id
                current_account_rows.append(current_account_dict)
        return LinkCurrentAccount.link_facade(current_account_rows, fk_institution_id)


    @classmethod
    def get_bank_account_from_csv(cls, bank_account_details):
        bank_account_number = re.search(BANK_ACCOUNT_REGEX_CSV, bank_account_details[BANK_ACCOUNT_NUMBER_INDEX]).group(1)
        bank_account_number_id = BankAccount.query.filter(BankAccount.account_number==bank_account_number).first()
        if not bank_account_number_id:
            raise Exception(f"There is no bank account with the account number {bank_account_number}.")
        return bank_account_number_id.id,bank_account_number_id.fk_institution_id




