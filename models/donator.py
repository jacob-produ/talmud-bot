from school_manager.db import db
from school_manager.models.crud_mixin import BaseMixin
from school_manager.models.income_source import DEFAULT_DONATOR_IS,IncomeSource

from school_manager.constants.constants_lists import UPLOAD_SOURCES
from datetime import datetime

class Donator(BaseMixin, db.Base):
    __tablename__ = "donator"
    __classnameheb__ = "תורם"
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(45))
    last_name = db.Column(db.String(45))
    billing_name = db.Column(db.String(45))
    identity = db.Column(db.String(45))
    mail = db.Column(db.String(100))
    state = db.Column(db.String(45))
    city = db.Column(db.String(45))
    street = db.Column(db.String(45))
    street_number = db.Column(db.String(45))
    type = db.Column(db.String(45))
    phone = db.Column(db.String(45))
    credit_four_digits = db.Column(db.Integer)

    data_source = db.Column(db.String(20), default=UPLOAD_SOURCES[0])
    data_upload_date = db.Column(db.DateTime, default=datetime.now)

    fk_income_source_id = db.Column(db.Integer, db.ForeignKey('income_source.id'))

    # Unique Constraints
    __table_args__ = (db.UniqueConstraint('credit_four_digits', 'identity', name='_donator_uc'),
                      db.CheckConstraint('NOT(identity IS NULL AND credit_four_digits IS NULL)', name='_donator_nn'))

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                {i: self.__dict__[i] for i in self.__dict__ if i != "_sa_instance_state"})


    @classmethod
    def create(cls, object_data, with_commit=True, many=False, ignore=''):
        fk_income_source_id = IncomeSource.read(name=DEFAULT_DONATOR_IS.get('name', ''), many=False).get('id')
        object_data['fk_income_source_id'] = fk_income_source_id
        if not object_data.get('identity'):
            object_data['identity'] = object_data.get('credit_four_digits')
        return super(Donator,cls).create(object_data=object_data, with_commit=with_commit, many=many, ignore=ignore)

    @classmethod
    def create_ignore(cls, object_data, with_commit=True, unique=[]):
        fk_income_source_id = IncomeSource.read(name=DEFAULT_DONATOR_IS.get('name', ''), many=False).get('id')
        for obj in object_data:
            obj['fk_income_source_id'] = fk_income_source_id
            if not obj.get('identity'):
                obj['identity'] = obj.get('credit_four_digits')
        return super(Donator,cls).create_ignore(object_data=object_data, with_commit=with_commit, unique=unique)
