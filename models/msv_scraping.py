from school_manager.db import db
from school_manager.models.crud_mixin import BaseMixin

from school_manager.constants.constants_lists import UPLOAD_SOURCES
from datetime import datetime


class MSVScraping(BaseMixin, db.Base):
    __tablename__ = "msv_scraping"
    __classnameheb__ = "מסב"
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    file_number = db.Column(db.Integer, nullable=False, unique=True)
    file_name = db.Column(db.String(45), nullable=True)
    institution_number = db.Column(db.Integer, nullable=False)
    transition_date = db.Column(db.DateTime, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    number_of_transaction = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(45), nullable=False)
    reference_number = db.Column(db.Integer, nullable=False)
    upload_date = db.Column(db.DateTime, nullable=False)
    upload_by = db.Column(db.String(45), nullable=False)

    data_source = db.Column(db.String(20), default=UPLOAD_SOURCES[0])
    data_upload_date = db.Column(db.DateTime, default=datetime.now)

    fk_institution_id = db.Column(db.Integer, db.ForeignKey('institution.id'),  nullable=False) # by msv_institute_code
    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                {i: self.__dict__[i] for i in self.__dict__ if i != "_sa_instance_state"})