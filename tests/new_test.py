"""
from school_manager.models.new_test import New_test
from werkzeug.security import generate_password_hash
from school_manager.db import db
from school_manager.db import initialize_db

initialize_db.init_db()

from school_manager.db import db
from flask_login import UserMixin
from school_manager.models.crud_mixin import BaseMixin


class New_test(BaseMixin, db.Base):

    __tablename__ = "New_test"
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    identity = db.Column(db.String(45), nullable=False)
    identity_type = db.Column(db.String(45), nullable=False)
    main_phone_number = db.Column(db.String(20), nullable=False)

    # Unique Constraints
    __table_args__ = (db.UniqueConstraint('identity', 'identity_type', name='_new_test_uc'),
                      db.UniqueConstraint('main_phone_number', name='new_test_uc'))


    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                {i: self.__dict__[i] for i in self.__dict__ if i != "_sa_instance_state"})


def create():
    new_test = New_test()
    new_test.identity = '312613627'
    new_test.identity_type = 'תעודת זהות'
    new_test.main_phone_number = '0544551239'

    db.session.add(new_test)
    db.session.commit()
    print("Test test was successfully done")


"""
# if __name__ == "__main__":
    # create()
