import random
import namegenerator
from school_manager.models.supplier import Supplier
from school_manager.db import db


def add_single_supplier():
    sup = Supplier()
    sup.name = namegenerator.gen().replace("-", " ").title()
    sup.identity = random.randint(100000000, 900000000)
    sup.classification = u'גבוה'

    db.session.add(sup)


if __name__ == "__main__":
    for i in range(10):
        add_single_supplier()
    db.session.commit()
    print("Done")
