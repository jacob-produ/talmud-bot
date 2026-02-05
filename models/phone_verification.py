from school_manager.db import db
from school_manager.models.crud_mixin import BaseMixin

from school_manager.constants.constants_lists import UPLOAD_SOURCES
from datetime import datetime


class OptVerification(BaseMixin, db.Base):
    __tablename__ = "opt_verification"
    __classnameheb__ = "אימות טלפוני"

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.now)
    response_status = db.Column(db.String(45))
    phone_number = db.Column(db.String(45))
    yafast_version = db.Column(db.String(45))
    verify_code = db.Column(db.String(45))
    caller_id = db.Column(db.String(45))
    calls_count = db.Column(db.Integer)
    billing_per_call = db.Column(db.Float)
    message = db.Column(db.String(220))
    verification_status = db.Column(db.String(45))
    verification_time = db.Column(db.String(45))
    billing = db.Column(db.Float)
    number_of_experiments = db.Column(db.Integer)
    source = db.Column(db.String(220))
    user_agent = db.Column(db.String(220))
    ip_address = db.Column(db.String(45))
    errors = db.Column(db.String(220))

    data_source = db.Column(db.String(20), default=UPLOAD_SOURCES[0])
    data_upload_date = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                {i: self.__dict__[i] for i in self.__dict__ if i != "_sa_instance_state"})
