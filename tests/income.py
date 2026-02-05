import datetime
from school_manager.models.income import Income
from school_manager.db import db

inc = Income()
inc.deposit_date = datetime.datetime.utcnow().isoformat()
inc.amount = 8846.56
inc.attribution = 'student'
inc.attribution_id = 3
# inc.type = u'תרומה'
inc.payment_reason = None
inc.fk_bank_account_id=1
inc.fk_income_source_id = 1
inc.fk_institution_id=3
inc.fk_branch_id=2
inc.fk_trend_coordinator_id = 1
inc.method = u"צ'ק"
inc.aid_fund_allotment = 1200
inc.test_fund_allotment = 30
inc.teaching_fund_allotment = None
inc.excellence_fund_allotment = None
inc.for_month = datetime.datetime(2020,9,21,1,1,1)
inc.fund_raiser = u'מגייס'

db.session.add(inc)
db.session.commit()

print("Test income was successfully done")