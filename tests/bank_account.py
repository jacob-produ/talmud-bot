from school_manager.models.bank_account import BankAccount
from school_manager.models.institution import Institution

from school_manager.db import db
from werkzeug.security import generate_password_hash

ba = BankAccount()
ba.bank_number = 972
ba.branch_name = u'בבליס'
ba.branch_number = 156746
ba.account_number = '0075649823'
ba.city = u'ירושלים'
ba.street = u'יהושוע'
ba.phone_number = '08-64112314'
ba.street_number = 206
ba.username = "Yosi22"
ba.password = generate_password_hash("0123456")
ba.signature_image = "Signature.JPG"
ba.fk_institution_id = Institution.query.filter().first().id
ba.line_of_credit = 300

db.session.add(ba)
db.session.commit()

print("Done")
