from school_manager.db import db
from school_manager.models.crud_mixin import BaseMixin
from school_manager.models.general_bank_account import GeneralBankAccount
from school_manager.constants import constants
from core.messages import CREATE_FAIL,CREATE_SUCCESS

from school_manager.constants.constants_lists import UPLOAD_SOURCES
from datetime import datetime

NAME_COL = "שם"
IDENTITY_COL = "מזהה"
BANK_NUMBER_COL = "מספר בנק"
BRANCH_NUMBER_COL = "מספר סניף"
BANK_ACCOUNT_NUMBER_COL = "מספר חשבון"
PHONE_COL = "טלפון"
MAIL_COL = "מייל"
AGENT_COL = "שם סוכן"
AGENT_PHONE_COL = "טלפון סוכן"
CLASSIFICATION_COL = "תחום"


class Supplier(BaseMixin, db.Base):
    __tablename__ = "supplier"
    __classnameheb__ = "ספק"
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=False)
    identity = db.Column(db.String(45), nullable=False)
    classification = db.Column(db.String(45), nullable=False)
    # The method which the chain use to pay the supplier
    payment_method = db.Column(db.String(20))
    phone_number = db.Column(db.String(20))
    mail = db.Column(db.String(40))
    agent_name = db.Column(db.String(45))
    agent_phone = db.Column(db.String(20))

    data_source = db.Column(db.String(20), default=UPLOAD_SOURCES[0])
    data_upload_date = db.Column(db.DateTime, default=datetime.now)

    @classmethod
    def create_supplier_from_csv(cls, csv_reader):
        supplier_records = []
        for row in csv_reader:
            identity = row.get(IDENTITY_COL)
            supplier = cls.read(identity=identity, many=False)
            if not supplier.get('id'):
                supplier_params = dict(name=row.get(NAME_COL),identity=identity,phone_number=row.get(PHONE_COL),
                                mail=row.get(MAIL_COL),agent_name=row.get(AGENT_COL),agent_phone=row.get(AGENT_PHONE_COL),
                                classification=row.get(CLASSIFICATION_COL))
                supplier_records.append(supplier_params)

        return cls.create_ignore(supplier_records)


    @classmethod
    def create(cls, object_data, with_commit=True, many=False, ignore=''):
        try:
            identity = str(int(object_data.get('identity')))
            object_data['identity'] = identity
        except ValueError as e:
            pass
        return super(Supplier,cls).create(object_data=object_data, with_commit=with_commit, many=many, ignore=ignore)

    @classmethod
    def create_ignore(cls, object_data, with_commit=True, unique=[]):
        for obj in object_data:
            try:
                identity = str(int(obj.get('identity')))
                obj['identity'] = identity
            except ValueError as e:
                pass
        return super(Supplier,cls).create_ignore(object_data=object_data, with_commit=with_commit, unique=unique)

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                {i: self.__dict__[i] for i in self.__dict__ if i != "_sa_instance_state"})