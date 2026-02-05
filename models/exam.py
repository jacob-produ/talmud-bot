from school_manager.db import db
from school_manager.models.crud_mixin import BaseMixin


class Exam(BaseMixin, db.Base):
    __tablename__ = "exam"
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    examiner_id = db.Column(db.Integer, nullable=False)
    student_id = db.Column(db.Integer, nullable=False)
    exam_result = db.Column(db.Integer, nullable=False)
    exam_number = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                {i: self.__dict__[i] for i in self.__dict__ if i != "_sa_instance_state"})