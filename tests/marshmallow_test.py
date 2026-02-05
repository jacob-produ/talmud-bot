import datetime
from school_manager.models.income import Income
from school_manager.db import initialize_db

initialize_db.init_db()


def create():
    # for_month = datetime.date(2020,1,1).isoformat()
    for_month = datetime.datetime(2020,1,1).isoformat()
    incs = [{"fk_source_id": 116,
           "attribution": "student",
           "attribution_id": 0,
           'amount': 300,
           'payment_reason': "שוטף",
           'fk_branch_id': 1,
           'for_month': for_month},

           {"fk_source_id": 1117,
            "attribution": "student",
            "attribution_id": 0,
            'amount': 300,
            'payment_reason': "שוטף",
            'fk_branch_id': 1,
            'for_month': for_month}
           ]

    print(Income.create(incs, many=True))


def read():
    print(Income.read())


if __name__ == "__main__":
    # create()
    read()

