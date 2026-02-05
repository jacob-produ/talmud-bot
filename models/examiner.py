from school_manager.db import db
from school_manager.models.crud_mixin import BaseMixin


class Examiner(BaseMixin, db.Base):
    __tablename__ = "examiner"
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(45), nullable=False)
    last_name = db.Column(db.String(45), nullable=False)
    payment_method = db.Column(db.String(20))

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                {i: self.__dict__[i] for i in self.__dict__ if i != "_sa_instance_state"})