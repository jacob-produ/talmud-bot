from school_manager.models.branch import Branch
from school_manager.models.institution import Institution
from school_manager.db import initialize_db
from school_manager.db import db

initialize_db.init_db()


def add_single_institution():
    inst = Institution()
    inst.name = u'הדר יוסף'
    inst.identity = u'500000000'

    db.session.add(inst)
    db.session.commit()

    # Add Branch
    br = Branch()
    br.fk_institution_id = inst.id
    br.symbol = 0

    db.session.add(br)
    db.session.commit()


def add_institutions():
    institutions = [
        {"name": "הדר יוסף", "identity": "500000000",
         "branches": [{"symbol": 0}, {"symbol": 2}]},

        {"name": "הדר דוד", "identity": "9856237",
         "branches": [{"symbol": 0}, {"symbol": 1}]},

         {"name": "הדר אברהם", "identity": "753951852",
          "branches": [{"symbol": 1}, {"symbol": 2}]}
    ]
    for institution in institutions:
        # Add Institution
        inst = Institution()

        inst.name = institution["name"]
        inst.identity = institution["identity"]

        db.session.add(inst)
        db.session.commit()

        for branch in institution["branches"]:
            # Add Branch
            br = Branch()
            br.fk_institution_id = inst.id
            br.symbol = branch["symbol"]

            db.session.add(br)
        db.session.commit()


def query_institution():
    # q = Institution.query.filter(Institution.identity==2, Institution.branches.any(Branch.symbol == 2))
    q = Branch.query.filter(Branch.symbol == 2, Branch.institution.has(Institution.identity == 2))
    for branch in q:
        print(branch)


def income_csv_institution_regex():
    import re
    institution_details = "מוסד: 500000000  הדר יוסף סניף 00"
    regex = re.search(r"\s(\d+).*?\s(\d+)", institution_details)
    print(regex.group(1))
    print(regex.group(2))


if __name__ == "__main__":
    Institution.get_institutions_branches_symbol_map()
    # add_institutions()
    # query_institution()
    # income_csv_institution_regex()
