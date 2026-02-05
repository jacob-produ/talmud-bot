from school_manager.models.trend_coordinator import TrendCoordinator
from school_manager.db import db

tc = TrendCoordinator()

tc.name = u"יוסי"
tc.created_by_user = u'יוסי'
tc.study_framework = u'מסגרת לימוד'
tc.study_program = u'תוכנית לימוד'
tc.profession = u'מקצוע'
tc.done_by_user = u'נוצר על ידי המשתמש'
tc.education = u'חינוך'
tc.eligibility_method = u'שיטת התאמה'
tc.eligibility_level = u'מתאים מאוד'
tc.excellence_scholarship = 600
tc.base_scholarship = 8000
tc.test_scholarship = 20450
tc.teaching_scholarship = None

db.session.add(tc)
db.session.commit()

print("Done")