import random
import namegenerator
from school_manager.models.employee import Employee
from school_manager.db import db


def add_single_employee():
    generated_name = namegenerator.gen().split('-')
    emp = Employee()
    # Institution test contains three institutions
    emp.fk_institution_id = random.randint(1, 3)
    emp.first_name = generated_name[0].title()
    emp.last_name = generated_name[1].title()
    emp.identity = random.randint(100000000, 900000000)
    db.session.add(emp)


if __name__ == "__main__":
    for i in range(20):
        add_single_employee()
    db.session.commit()
    print("Done")
