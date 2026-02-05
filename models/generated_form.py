from school_manager.db import db
from school_manager.models.crud_mixin import BaseMixin


class GeneratedForm(BaseMixin, db.Base):
    __tablename__ = "generated_form"
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    fk_form_template_id = db.Column(db.Integer, db.ForeignKey('form_template.id'))
    fk_student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    fk_enrollment_id = db.Column(db.Integer, db.ForeignKey('course_enrollment.id'))
    fk_institution_id = db.Column(db.Integer, db.ForeignKey('institution.id'))

    payment_amount = db.Column(db.Float)
    form_status = db.Column(db.String(45))
    shipping_option = db.Column(db.String(45))
    application_date = db.Column(db.DateTime)
    form_generation_date = db.Column(db.DateTime)

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                {i: self.__dict__[i] for i in self.__dict__ if i != "_sa_instance_state"})