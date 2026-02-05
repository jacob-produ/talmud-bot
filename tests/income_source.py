from school_manager.models.income_source import IncomeSource
from school_manager.db import db

inc_src = IncomeSource()

inc_src.name = u'רוביק'
inc_src.type = "תקצוב עירוני"
inc_src.aid_fund_allotment = None
inc_src.test_fund_allotment = None
inc_src.teaching_fund_allotment = 6000
inc_src.excellence_fund_allotment = 450623
inc_src.fund_raiser = u'מגייס ב'

db.session.add(inc_src)
db.session.commit()

print("Done")