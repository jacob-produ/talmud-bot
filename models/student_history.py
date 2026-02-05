from school_manager.db import db
from school_manager.models.crud_mixin import BaseMixin



class StudentHistory(BaseMixin, db.Base):
    __tablename__ = "student_history"
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    identity = db.Column(db.String(45), nullable=False)
    identity_type = db.Column(db.String(45), nullable=False)
    fk_student_id = db.Column(db.Integer, db.ForeignKey('student.id'))

    # Unique Constraints
    __table_args__ = (db.UniqueConstraint('identity','identity_type',  name='_student_uc'),)