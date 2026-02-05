from school_manager.db import db
from school_manager.models.crud_mixin import BaseMixin

from school_manager.constants.constants_lists import UPLOAD_SOURCES
from datetime import datetime


class MSVScrapingInner(BaseMixin, db.Base):
    __tablename__ = "msv_scraping_inner"
    __classnameheb__ = "מסב פנימי"

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    row_number = db.Column(db.Integer, nullable=False)
    identity = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(45), nullable=False)
    branch_number = db.Column(db.Integer, nullable=False)
    bank_number = db.Column(db.Integer, nullable=False)
    account_number = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    reference_number = db.Column(db.Integer, nullable=False, unique=True)


    data_source = db.Column(db.String(20), default=UPLOAD_SOURCES[0])
    data_upload_date = db.Column(db.DateTime, default=datetime.now)

    fk_msv_scraping_id = db.Column(db.Integer, db.ForeignKey('msv_scraping.id'), nullable=False)
    fk_student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    fk_supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                {i: self.__dict__[i] for i in self.__dict__ if i != "_sa_instance_state"})