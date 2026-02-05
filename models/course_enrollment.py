import datetime
from school_manager.db import db
from school_manager.models.crud_mixin import BaseMixin
from school_manager.models.trend_coordinator import TrendCoordinator
from school_manager.models.trend_coordinator_attribution import TrendCoordinationAttribution
from school_manager.constants.course_types import COURSE_TYPE_DAY_PART_MAP

from school_manager.constants.constants_lists import UPLOAD_SOURCES
from datetime import datetime

class CourseEnrollment(BaseMixin, db.Base):
    __tablename__ = "course_enrollment"
    __classnameheb__ = "רישום לקורסים"
    # Columns
    id = db.Column(db.Integer, primary_key=True)

    # morning, morning-noon, noon, whole day
    course_type = db.Column(db.Integer, nullable=False)
    profession = db.Column(db.String(45))
    registration_date = db.Column(db.DateTime, nullable=True)
    registration_status = db.Column(db.String(45), default='ממתין לשיבוץ')
    start_date = db.Column(db.DateTime, default=datetime.today)
    end_date = db.Column(db.DateTime, nullable=True)
    enrollment_status = db.Column(db.Boolean)

    data_source = db.Column(db.String(20), default=UPLOAD_SOURCES[0])
    data_upload_date = db.Column(db.DateTime, default=datetime.now)

    fk_student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    fk_branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'), nullable=False)

    # Unique Constraints
    __table_args__ = (db.UniqueConstraint('course_type', 'fk_student_id','fk_branch_id', name='_course_uc'),)

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                {i: self.__dict__[i] for i in self.__dict__ if i != "_sa_instance_state"})



    @classmethod
    def get_last_enrollments(cls, num_of_enrollments):
        query_result = db.session.query(cls).order_by(cls.id.desc()).limit(num_of_enrollments)
        return cls.Schema(many=True).dump(query_result)

    @classmethod
    def update_trend_attributions(cls, trend_attributions, ce_id):
        for ta in trend_attributions:
            TrendCoordinationAttribution.update(dict(fk_course_enrollment=None), id=ta.get('id'))
        last_trend_coordinator = {**trend_attributions[-1], **dict(fk_course_enrollment_id=ce_id)}
        del last_trend_coordinator['id']
        TrendCoordinationAttribution.create(last_trend_coordinator)

    @classmethod
    def create_default_trend_attribution(cls, ce_id, day_part, start_date, student_id, default_trend_coordinator_id):
        new_attribution_record = dict(day_part=day_part, start_date=start_date, fk_student_id=student_id,
                                      fk_course_enrollment_id=ce_id,
                                      fk_trend_coordinator_id=default_trend_coordinator_id)
        trend_attribution = TrendCoordinationAttribution.create(new_attribution_record)
        print(trend_attribution)

    @classmethod
    def attribute_course_enrollment_to_trend_coordinator(cls, course_enrollments: list):
        default_trend_coordinator_id = TrendCoordinator.get_default_trend_coordinator_id()
        for ce in course_enrollments:
            ce_id, course_type, start_date, student_id = ce.get('id'), ce.get('course_type'), ce.get(
                'start_date'), ce.get('fk_student_id')

            day_part_list = COURSE_TYPE_DAY_PART_MAP.get(course_type, [])
            query_result = db.session.query(TrendCoordinationAttribution).filter(
                TrendCoordinationAttribution.day_part.in_(day_part_list),
                TrendCoordinationAttribution.fk_student_id == student_id,
                TrendCoordinationAttribution.start_date <= start_date)
            trend_attributions = TrendCoordinationAttribution.Schema(many=True).dump(query_result)
            if trend_attributions:
                cls.update_trend_attributions(trend_attributions,ce_id)
            else:
                cls.create_default_trend_attribution(ce_id, day_part_list[0], start_date, student_id,
                                                     default_trend_coordinator_id)
