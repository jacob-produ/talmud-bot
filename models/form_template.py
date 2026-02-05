from school_manager.db import db
from school_manager.models.crud_mixin import BaseMixin


class FormTemplate(BaseMixin, db.Base):
    __tablename__ = "form_template"
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45))
    template_path = db.Column(db.String(9999))
    applicable_min_age = db.Column(db.Integer)
    applicable_max_age = db.Column(db.Integer)
    applicable_identity_type = db.Column(db.String(45))
    applicable_marital_status = db.Column(db.String(45))

    @classmethod
    def get_all_forms_dict(cls):
        forms_list = cls.read(many=True)
        return {form.get('id'): form for form in forms_list}


    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                {i: self.__dict__[i] for i in self.__dict__ if i != "_sa_instance_state"})