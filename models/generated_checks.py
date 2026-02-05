from school_manager.db import db
from school_manager.models.crud_mixin import BaseMixin


class GeneratedChecks(BaseMixin, db.Base):
    __tablename__ = "examiner"
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    institution_id = db.Column(db.String(45), nullable=False)
    employee_id = db.Column(db.String(45), nullable=False)
    bank_account_num = db.Column(db.String(20))

