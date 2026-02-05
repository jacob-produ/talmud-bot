from school_manager.db import db
from school_manager.models.crud_mixin import BaseMixin


class PaymentFailureCode(BaseMixin, db.Base):
    __tablename__ = "payment_failure_code"
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Integer, unique=True)
    description = db.Column(db.String(45))
    action = db.Column(db.String(45))

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                {i: self.__dict__[i] for i in self.__dict__ if i != "_sa_instance_state"})