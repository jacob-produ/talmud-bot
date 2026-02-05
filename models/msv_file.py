import datetime
from school_manager.db import db
from school_manager.models.crud_mixin import BaseMixin
from school_manager.modules.masav import masav


class MSVFile(BaseMixin, db.Base):
    __tablename__ = "msv_file"
    __classnameheb__ = "קובץ מסב"
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float,  nullable=True)
    date = db.Column(db.DateTime, nullable=True)
    file_name = db.Column(db.String(400), nullable=True)
