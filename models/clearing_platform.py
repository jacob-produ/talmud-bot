from school_manager.db import db
from school_manager.models.crud_mixin import BaseMixin

from school_manager.constants.constants_lists import UPLOAD_SOURCES
from datetime import datetime

#TODO: add unique constraint
class ClearingPlatform(BaseMixin, db.Base):
    __tablename__ = "clearing_platform"
    __classnameheb__ = "פלטפורמת סליקה"
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), unique=True)

    data_source = db.Column(db.String(20), default=UPLOAD_SOURCES[0])
    data_upload_date = db.Column(db.DateTime, default=datetime.now)

    fk_bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_account.id'), nullable=False)
    fk_trend_coordinator_id = db.Column(db.Integer, db.ForeignKey('trend_coordinator.id'), nullable=False)

    # Unique Constraints
    __table_args__ = (db.UniqueConstraint('name', name='_name_uc'),)

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                {i: self.__dict__[i] for i in self.__dict__ if i != "_sa_instance_state"})