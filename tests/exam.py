import datetime
from school_manager.models.exam import Exam
from school_manager.db import db

exams = Exam()
exams.date = datetime.date.today()
exams.examiner_id = 4
exams.student_id = 20
exams.exam_result = 80
exams.exam_number = 3

db.session.add(exams)
db.session.commit()


print("Test exams was successfully done")