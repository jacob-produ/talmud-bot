import datetime
from school_manager.models.student import Student
from school_manager.db import db


def add_student():
    stu = Student()

    stu.fk_branch_id = 1
    stu.fk_trend_coordinator_id = 1
    stu.first_name = u'יוסי'
    stu.last_name = u'טל'
    stu.identity = u'זהות'
    stu.identity_type = u'סוג זהות'
    stu.birth_date = datetime.date.today()
    stu.course_type = u'מעשי'
    stu.profession = u'בינה מלאכותית'
    stu.fund_raiser = u'מגייס'
    stu.eligibility_method = u"שיטת התאמה"
    stu.eligibility_level = u"מתאים ביותר"
    stu.excellence_scholarship = "מלגת הצטיינות"
    stu.base_scholarship = None
    stu.teaching_scholarship = None

    db.session.add(stu)
    db.session.commit()


def query_student():
    identity = "207130000"
    course_type = "100"
    fk_branch_id = "1"
    student = Student.query.filter_by(identity=identity, fk_branch_id=fk_branch_id, course_type=course_type).first()
    return student.id


if __name__ == "__main__":
    query_student()

