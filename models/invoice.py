from school_manager.db import db
from school_manager.models.crud_mixin import BaseMixin

from school_manager.constants.constants_lists import UPLOAD_SOURCES
from datetime import datetime

class Invoice(BaseMixin, db.Base):
    __tablename__ = "invoice"
    __classnameheb__ = "חשבונית"
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    invoice_date = db.Column(db.DateTime, nullable=False)
    invoice_number = db.Column(db.String(45), nullable=False)
    payment_due_date = db.Column(db.DateTime, nullable=True)
    invoice_file_name =  db.Column(db.String(500), nullable=True)

    data_source = db.Column(db.String(20), default=UPLOAD_SOURCES[0])
    data_upload_date = db.Column(db.DateTime, default=datetime.now)

    fk_expense_id = db.Column(db.Integer, db.ForeignKey('expense.id'))


    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                {i: self.__dict__[i] for i in self.__dict__ if i != "_sa_instance_state"})
