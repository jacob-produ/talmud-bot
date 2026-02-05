from school_manager.db import db
from school_manager.models.crud_mixin import BaseMixin


class CommitteeMember(BaseMixin, db.Base):
    __tablename__ = "committee_member"
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    identity = db.Column(db.String(45), nullable=False)
    first_name = db.Column(db.String(45))
    last_name = db.Column(db.String(45))
    role = db.Column(db.String(45))
    signature_image = db.Column(db.String(45))
    phone_number = db.Column(db.String(20))
    fk_institution_id = db.Column(db.Integer, db.ForeignKey('institution.id'))

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                {i: self.__dict__[i] for i in self.__dict__ if i != "_sa_instance_state"})