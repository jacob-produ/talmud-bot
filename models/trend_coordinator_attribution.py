from school_manager.db import db
from school_manager.models.crud_mixin import BaseMixin
from sqlalchemy.sql.operators import or_

from school_manager.constants.constants_lists import UPLOAD_SOURCES
from datetime import datetime

class TrendCoordinationAttribution(BaseMixin, db.Base):
    __tablename__ = "trend_coordinator_attribution"
    __classnameheb__ = "שיוך מנחה"
    # Columns
    id = db.Column(db.Integer, primary_key=True)

    fund_raiser = db.Column(db.String(45))
    excellence_scholarship = db.Column(db.String(45))
    base_scholarship = db.Column(db.String(45))
    teaching_scholarship = db.Column(db.String(45))
    default_scholarship = db.Column(db.Boolean, default=False)
    scholarship_method = db.Column(db.String(45))
    start_date = db.Column(db.DateTime, default=datetime.today)
    end_date = db.Column(db.DateTime, nullable=True)

    payment_method = db.Column(db.String(20))
    eligibility_min = db.Column(db.Integer)
    eligibility_method = db.Column(db.String(45))
    eligibility_level = db.Column(db.Integer, default=0)
    day_part = db.Column(db.String(15))

    data_source = db.Column(db.String(20), default=UPLOAD_SOURCES[0])
    data_upload_date = db.Column(db.DateTime, default=datetime.now)

    fk_student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    fk_trend_coordinator_id = db.Column(db.Integer, db.ForeignKey('trend_coordinator.id'), nullable=False)
    fk_course_enrollment_id = db.Column(db.Integer, db.ForeignKey('course_enrollment.id'), nullable=True)

    # Unique Constraints
    __table_args__ = (db.UniqueConstraint('fk_course_enrollment_id', 'day_part', name='_trend_attribution_uc'),)

    # Relationship
    course_enrollments = db.relationship('CourseEnrollment', uselist=True)
    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                {i: self.__dict__[i] for i in self.__dict__ if i != "_sa_instance_state"})


    @classmethod
    def get_last_enrollments(cls, num_of_attributions):
        query_result = db.session.query(cls).order_by(cls.id.desc()).limit(num_of_attributions)
        return cls.Schema(many=True).dump(query_result)




    @classmethod
    def attribute_trend_coordinator_to_course_enrollment(cls, trend_attributions: list):
        from school_manager.models.course_enrollment import CourseEnrollment
        from school_manager.constants.course_types import COURSE_TYPE_DAY_PART_MAP_REVERSED
        from school_manager.modules.exceptions import CourseEnrollmentAttributionError
        attribution_errors = []
        for ta in trend_attributions:
            try:
                day_part, start_date, student_id = ta.get('day_part'), ta.get(
                    'start_date'), ta.get('fk_student_id')

                course_type_list = COURSE_TYPE_DAY_PART_MAP_REVERSED.get(day_part, [])
                query_result = db.session.query(CourseEnrollment).filter(
                    CourseEnrollment.course_type.in_(course_type_list),
                    CourseEnrollment.fk_student_id == student_id,
                    or_(CourseEnrollment.start_date >= start_date,
                        CourseEnrollment.start_date == None))
                course_enrollments = CourseEnrollment.Schema(many=True).dump(query_result)
                if course_enrollments:
                    cls.update(dict(fk_course_enrollment_id=course_enrollments[-1].get('id')), id=ta.get('id'))
                else:
                    raise CourseEnrollmentAttributionError(ta.get('id'))
            except CourseEnrollmentAttributionError as e:
                attribution_errors.append(dict(error=str(e), data=ta))
            except Exception as e:
                attribution_errors.append(dict(error=str(e), data=ta))
        return attribution_errors
