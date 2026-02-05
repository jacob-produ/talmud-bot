from school_manager.models.branch import Branch
from school_manager.db import db

br = Branch()
br.fk_institution_id = 1
br.symbol = 2

db.session.add(br)
db.session.commit()

print("Done")