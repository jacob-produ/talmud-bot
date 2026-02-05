from school_manager.db import db
from school_manager.models.crud_mixin import BaseMixin

from school_manager.constants.constants_lists import UPLOAD_SOURCES
from datetime import datetime

class PaymentFailure(BaseMixin, db.Base):
    __tablename__ = "payment_failure"
    __classnameheb__ = "שגיאת הכנסה"

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    data_source = db.Column(db.String(20), default=UPLOAD_SOURCES[0])
    data_upload_date = db.Column(db.DateTime, default=datetime.now)

    fk_payment_failure_id = db.Column(db.Integer, db.ForeignKey('payment_failure_code.id'), nullable=False)
    fk_course_enrollment_id = db.Column(db.Integer, db.ForeignKey('course_enrollment.id'), nullable=False)
    fk_income_id = db.Column(db.Integer, db.ForeignKey('income.id'), nullable=False)

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                {i: self.__dict__[i] for i in self.__dict__ if i != "_sa_instance_state"})