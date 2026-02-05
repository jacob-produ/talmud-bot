from school_manager.db import db
from school_manager.models.crud_mixin import BaseMixin
from school_manager.models.institution import Institution

from school_manager.constants.constants_lists import UPLOAD_SOURCES
from datetime import datetime

class Branch(BaseMixin, db.Base):
    __tablename__ = "branch"
    __classnameheb__ = "סניף"
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.Integer, index=True, nullable=False)
    city = db.Column(db.String(45))
    street = db.Column(db.String(45))
    street_number = db.Column(db.String(45))
    start_date = db.Column(db.DateTime)
    first_opening_hour = db.Column(db.String(10))
    first_closing_hour = db.Column(db.String(10))
    second_opening_hour = db.Column(db.String(10))
    second_closing_hour = db.Column(db.String(10))
    shift_manager_first_name = db.Column(db.String(45))
    shift_manager_last_name = db.Column(db.String(45))
    first_contact_name = db.Column(db.String(45))
    second_contact_name = db.Column(db.String(45))
    first_contact_phone = db.Column(db.String(45))
    second_contact_phone = db.Column(db.String(45))
    comments = db.Column(db.String(320))
    school_description = db.Column(db.String(320))

    data_source = db.Column(db.String(20), default=UPLOAD_SOURCES[0])
    data_upload_date = db.Column(db.DateTime, default=datetime.now)

    fk_institution_id = db.Column(db.Integer, db.ForeignKey('institution.id'),  nullable=False)

    # Relationships
    institution = db.relationship('Institution', uselist=False)

    # Unique Constraints
    __table_args__ = (db.UniqueConstraint('fk_institution_id', 'symbol', name='_institution_symbol_uc'),)

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                {i: self.__dict__[i] for i in self.__dict__ if i != "_sa_instance_state"})


    @classmethod
    def get_branch_id_by_institution_and_symbol(cls,institution_identity,symbol):
        institution = Institution.get_institution_by_identity(institution_identity)
        if not institution:
            return institution
        branch = cls.read(many=False,fk_institution_id=institution.get('id'), symbol=symbol)
        return branch


