from school_manager.db import db
from school_manager.models.crud_mixin import BaseMixin

from school_manager.constants.constants_lists import UPLOAD_SOURCES
from datetime import datetime

class RegistrationForm(BaseMixin, db.Base):
    __tablename__ = "registration_form"
    __classnameheb__ = "אימות טלפוני"

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.now)
    day_part = db.Column(db.String(45))
    morning_sponsor_name = db.Column(db.String(45))
    noon_sponsor_name = db.Column(db.String(45))
    morning_sponsor_phone = db.Column(db.String(45))
    noon_sponsor_phone = db.Column(db.String(45))
    employee = db.Column(db.Boolean)
    employer_name = db.Column(db.String(45))
    amount = db.Column(db.Float)
    working_hours = db.Column(db.String(45))
    volunteer = db.Column(db.Boolean)
    # constants VOLUNTEER_HOURS
    volunteer_hours = db.Column(db.String(45))
    weekly_hours = db.Column(db.String(45))
    morning_location_name = db.Column(db.String(45))
    noon_location_name = db.Column(db.String(45))
    # row status = wrong or not
    row_status = db.Column(db.String(45))

    morning_online = db.Column(db.Boolean)
    afternoon_online = db.Column(db.Boolean)
    morning_in_town = db.Column(db.Boolean)
    afternoon_in_town = db.Column(db.Boolean)
    morning_location_description = db.Column(db.String(45))
    afternoon_location_description = db.Column(db.String(45))
    morning_occupation_description = db.Column(db.String(45))
    afternoon_occupation_description = db.Column(db.String(45))
    morning_integration = db.Column(db.String(45))
    afternoon_integration = db.Column(db.String(45))
    morning_availability = db.Column(db.String(45))
    afternoon_availability = db.Column(db.String(45))
    last_study_location = db.Column(db.String(45))

    study_also = db.Column(db.Boolean)
    institution_name = db.Column(db.String(45))
    number_of_hours = db.Column(db.Float)
    morning_column_number = db.Column(db.Integer)
    afternoon_column_number = db.Column(db.Integer)
    morning_row_number = db.Column(db.Integer)
    afternoon_row_number = db.Column(db.Integer)

    morning_volunteer_name = db.Column(db.String(45))
    afternoon_volunteer_name = db.Column(db.String(45))

    form_number = db.Column(db.Integer)
    registration_date = db.Column(db.DateTime)
    registration_status = db.Column(db.String(45))
    data_source = db.Column(db.String(20), default=UPLOAD_SOURCES[0])
    data_upload_date = db.Column(db.DateTime, default=datetime.now)

    fk_student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    fk_morning_trend_coordinator_personal_code = db.Column(db.Integer, db.ForeignKey('trend_coordinator.id'), nullable=False) # by personal_code
    fk_noon_trend_coordinator_id = db.Column(db.Integer, db.ForeignKey('trend_coordinator.id'), nullable=False)# by personal_code

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                {i: self.__dict__[i] for i in self.__dict__ if i != "_sa_instance_state"})