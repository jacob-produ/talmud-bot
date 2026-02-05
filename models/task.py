import datetime
from school_manager.db import db
from school_manager.models.crud_mixin import BaseMixin


class Task(BaseMixin, db.Base):
    __tablename__ = "task"
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    created_by_user = db.Column(db.Integer, nullable=False)
    done_by_user = db.Column(db.Integer, nullable=False)
    designed_for_user = db.Column(db.Integer, nullable=False)
    periodicity = db.Column(db.Integer, nullable=False)
    importance = db.Column(db.Integer, nullable=False)
    day_to_start = db.Column(db.DateTime, default=datetime.date.today, nullable=False)
    deadline = db.Column(db.DateTime, default=datetime.date.today, nullable=False)
    execution_date = db.Column(db.DateTime, default=datetime.date.today, nullable=False)

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                {i: self.__dict__[i] for i in self.__dict__ if i != "_sa_instance_state"})