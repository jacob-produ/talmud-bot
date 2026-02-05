from school_manager.db import db
from school_manager.models.crud_mixin import BaseMixin

from school_manager.constants.constants_lists import UPLOAD_SOURCES
from datetime import datetime


class Institution(BaseMixin, db.Base):
    __tablename__ = "institution"
    __classnameheb__ = "מוסד"
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=False)
    short_name = db.Column(db.String(20))
    identity = db.Column(db.String(45), index=True, nullable=False, unique=True)
    msv_institute_code = db.Column(db.Integer, nullable=False)
    msv_sending_institute_code = db.Column(db.Integer, nullable=False)
    city = db.Column(db.String(45), nullable=False)
    zip_code = db.Column(db.String(45), nullable=False)
    phone_number = db.Column(db.String(400), default="")
    capacity = db.Column(db.Integer, nullable=True)

    data_source = db.Column(db.String(20), default=UPLOAD_SOURCES[0])
    data_upload_date = db.Column(db.DateTime, default=datetime.now)
    # Relationships
    branches = db.relationship('Branch', uselist=True)
    bank_account = db.relationship('BankAccount', uselist=True)

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                {i: self.__dict__[i] for i in self.__dict__ if i != "_sa_instance_state"})

    @staticmethod
    def get_institutions_branches_symbol_map():
        institutions_branches_map = {}
        institutions = Institution.read()
        for institution in institutions:
            institutions_branches_map[institution["identity"]] = institution
            # Get branches by symbol dict
            institutions_branches_map[institution["identity"]]["branches"] = \
                {branch['symbol']: branch for branch in institution["branches"]}

        return institutions_branches_map

    @classmethod
    def get_institution_by_identity(cls, identity):
        return cls.read(many=False, identity=identity)
