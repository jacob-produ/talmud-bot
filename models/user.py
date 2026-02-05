from school_manager.db import db
from flask_login import UserMixin
from school_manager.models.crud_mixin import BaseMixin


class User(BaseMixin, db.Base, UserMixin):

    __tablename__ = "user"
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(45), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(45), nullable=False)
    last_name = db.Column(db.String(45), nullable=False)
    role = db.Column(db.String(45), nullable=False)
    deleted = db.Column(db.Boolean(), nullable=False, default=False)

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                {i: self.__dict__[i] for i in self.__dict__ if i != "_sa_instance_state"})