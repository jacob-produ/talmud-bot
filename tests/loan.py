from school_manager.models.loan import Loan
from school_manager.db import db

loans = Loan()

loans.fk_account_id = 1
loans.total_amount = 50000
loans.monthly_amount = 12000
loans.annual_interest = 6.87
loans.lender = u'בנק מזרחי'
loans.aid_fund_allotment = None
loans.test_fund_allotment = None
loans.teaching_fund_allotment = 15000
loans.excellence_fund_allotment = None

db.session.add(loans)
db.session.commit()

print("Test loans was successfully done")