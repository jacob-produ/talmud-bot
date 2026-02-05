from school_manager.db import db
from school_manager.models.crud_mixin import BaseMixin
from school_manager.models.trend_coordinator_nickname import TrendCoordinatorNickname


from school_manager.constants.constants_lists import UPLOAD_SOURCES
from datetime import datetime

DEFAULT_TREND_COORDINATOR = {
    'name': 'ללא מנחה'
}

class TrendCoordinator(BaseMixin, db.Base):
    __tablename__ = "trend_coordinator"
    __classnameheb__ = "מנחה"
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=False, unique=True)
    created_by_user = db.Column(db.String(45))
    study_framework = db.Column(db.String(45))
    study_program = db.Column(db.String(45))
    profession = db.Column(db.String(45))
    done_by_user = db.Column(db.String(45))
    education = db.Column(db.String(45))
    city = db.Column(db.String(45))
    street = db.Column(db.String(45))
    street_number = db.Column(db.String(45))
    home_city = db.Column(db.String(45))
    home_street = db.Column(db.String(45))
    home_street_number = db.Column(db.String(45))
    mail = db.Column(db.String(45))
    phone = db.Column(db.String(45))
    second_phone = db.Column(db.String(45))
    first_opening_hour = db.Column(db.String(10))
    first_closing_hour = db.Column(db.String(10))
    second_opening_hour = db.Column(db.String(10))
    second_closing_hour = db.Column(db.String(10))
    examiner_name = db.Column(db.String(45))
    default_payment_method = db.Column(db.String(45))
    contact_name = db.Column(db.String(45))
    contact_phone = db.Column(db.String(45))
    coordination_middleman_name = db.Column(db.String(45))

    excellence_scholarship = db.Column(db.Integer)
    base_scholarship = db.Column(db.Integer)
    test_scholarship = db.Column(db.Integer)
    teaching_scholarship = db.Column(db.Integer)
    scholarship_method = db.Column(db.String(45))
    # Allotment
    eligibility_min = db.Column(db.Integer)
    eligibility_method = db.Column(db.String(45))
    eligibility_level = db.Column(db.Integer, default=0)

    platform_fee = db.Column(db.Float, default=0)
    target_audience = db.Column(db.String(20))

    google_sheet_url = db.Column(db.String(250))

    personal_code = db.Column(db.String(220))
    password = db.Column(db.String(220))

    study_hours_range = db.Column(db.String(45))

    active = db.Column(db.Boolean, default=True)

    data_source = db.Column(db.String(20), default=UPLOAD_SOURCES[0])
    data_upload_date = db.Column(db.DateTime, default=datetime.now)


    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                {i: self.__dict__[i] for i in self.__dict__ if i != "_sa_instance_state"})

    @classmethod
    def get_trend_coordinator_by_name(cls, name, many=True):
        trend_coordinator = cls.read(many=many, name=name)
        if trend_coordinator:
            return trend_coordinator
        trend_coordinator_nickname = TrendCoordinatorNickname.read(many=False, nickname=name)
        if not trend_coordinator_nickname.get('id'):
            return trend_coordinator_nickname
        return cls.read(many=many, id=trend_coordinator_nickname.get('id'))

    @classmethod
    def get_default_trend_coordinator_id(cls):
        return cls.read(name=DEFAULT_TREND_COORDINATOR.get('name'), many=False).get('id')

