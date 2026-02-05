from school_manager.models.examiner import Examiner
from school_manager.db import db

examiners = Examiner()
examiners.first_name = 'Tomer'
examiners.last_name = 'Tal'
db.session.add(examiners)
db.session.commit()

print("Test examiners was successfully done")