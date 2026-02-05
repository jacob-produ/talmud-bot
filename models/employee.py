from school_manager.db import db
from school_manager.models.crud_mixin import BaseMixin
from school_manager.models.institution import Institution

class Employee(BaseMixin, db.Base):
    __tablename__ = "employee"
    __classnameheb__ = "עובד"
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    fk_institution_id = db.Column(db.Integer, db.ForeignKey('institution.id'))
    first_name = db.Column(db.String(45), nullable=False)
    identity = db.Column(db.String(45), nullable=False)
    last_name = db.Column(db.String(45), nullable=False)
    # The method which the chain use to pay the employee's salary
    payment_method = db.Column(db.String(20))


    @classmethod
    def create(cls, object_data, with_commit=True, many=False, ignore=''):
        try:
            identity = str(int(object_data.get('identity')))
            object_data['identity'] = identity
        except ValueError as e:
            pass
        return super(Employee,cls).create(object_data=object_data, with_commit=with_commit, many=many, ignore=ignore)

    @classmethod
    def create_ignore(cls, object_data, with_commit=True, unique=[]):
        for obj in object_data:
            try:
                identity = str(int(obj.get('identity')))
                obj['identity'] = identity
            except ValueError as e:
                pass
        return super(Employee,cls).create_ignore(object_data=object_data, with_commit=with_commit, unique=unique)

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                {i: self.__dict__[i] for i in self.__dict__ if i != "_sa_instance_state"})