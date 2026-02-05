import csv
from io import StringIO
from core import messages
from flask import request, jsonify
from flask_restful import Resource
from school_manager.constants import constants

from school_manager.models.branch import Branch
from school_manager.models.institution import Institution
from school_manager.models.trend_coordinator import TrendCoordinator

from school_manager.constants.constants import UT8_WITH_BOM_ENCODING
from school_manager.routes.auth import login_required

INS_BR_COORD_CSV_PARAMETER = "institutions_branches_trend_coordinators_csv"

INSTITUTION_NAME_COL = "שם מוסד"
INSTITUTION_IDENTITY_COL = "זהות המוסד"
INSTITUTION_CITY_COL = "עיר המוסד"
INSTITUTION_ZIP_COL = "מיקוד המוסד"
INSTITUTION_MSV_CODE = "קוד מסב"
INSTITUTION_SENDING_MSV_CODE = "קוד מסב שולח"

BRANCH_SYMBOL_COL = "סמל הסניף"
BRANCH_INSTITUTION_COL = "מוסד הסניף"

TREND_COORDINATOR_NAME_COL = "שם מנחה"
ELIGIBILITY_METHOD = "eligibility_method"
ELIGIBILITY_MIN = "eligibility_min"
ELIGIBILITY_LEVEL ="eligibility_level"

def convert_to_integer(val):
    try:
        val = int(val)
    except ValueError as e:
        val = None
    return val


def create_inst_br_coord_from_csv(csv_reader):
    branches_temp = []
    institutions = []
    branches = []
    coordinators = []
    response = {}
    for row in csv_reader:
        # Add institution from row to db
        if row[INSTITUTION_IDENTITY_COL] and row[INSTITUTION_NAME_COL] and row[INSTITUTION_CITY_COL] and row[INSTITUTION_ZIP_COL]:
            institutions.append(dict(name=row[INSTITUTION_NAME_COL],
                                     identity=row[INSTITUTION_IDENTITY_COL],
                                     msv_institute_code=row[INSTITUTION_MSV_CODE],
                                     msv_sending_institute_code=row[INSTITUTION_SENDING_MSV_CODE],
                                     city=row[INSTITUTION_CITY_COL],
                                     zip_code=row[INSTITUTION_ZIP_COL]
                                     ))

        # Add trend_coordinator from row to db
        if row[TREND_COORDINATOR_NAME_COL]:
            eligibility_method = row[ELIGIBILITY_METHOD] if len(row[ELIGIBILITY_METHOD]) != 0 else None
            eligibility_min = convert_to_integer(row[ELIGIBILITY_MIN])
            eligibility_level = convert_to_integer(row[ELIGIBILITY_LEVEL])
            coordinators.append(dict(name=row[TREND_COORDINATOR_NAME_COL], eligibility_method=eligibility_method,eligibility_min=eligibility_min,
                                     eligibility_level=eligibility_level))

        # Add branch from row to list
        if row[BRANCH_SYMBOL_COL] and row[BRANCH_INSTITUTION_COL]:
            branches_temp.append((row[BRANCH_SYMBOL_COL], row[BRANCH_INSTITUTION_COL]))

    response["institutions"] = Institution.create_ignore(institutions, with_commit=True, unique=[Institution.name])
    response["trend_coordinators"] = TrendCoordinator.create_ignore(coordinators, with_commit=True, unique=[TrendCoordinator.name])

    institutions_branches_map = Institution.get_institutions_branches_symbol_map()

    for branch in branches_temp:
        # Add branch from list to db
        branches.append(dict(symbol=branch[0],
                             fk_institution_id=institutions_branches_map.get(branch[1], {}).get('id', None)))

    response["branches"] = Branch.create_ignore(branches, with_commit=True)

    return response


class InstitutionBranchCoordinatorAPI(Resource):
    @staticmethod
    @login_required()
    def get():
        return jsonify(Institution.get_institutions_branches_symbol_map())

    @staticmethod
    @login_required()
    def post():
        # Add from csv file
        if request.files and INS_BR_COORD_CSV_PARAMETER in request.files:
            csv_file = request.files[INS_BR_COORD_CSV_PARAMETER]
            if not csv_file.filename:
                return {constants.STR_MESSAGE: messages.REQUEST_EMPTY_FILE_ERROR, constants.STR_ERROR: True}
            csv_data = StringIO(csv_file.read().decode(UT8_WITH_BOM_ENCODING))
            csv_reader = csv.DictReader(csv_data)
            return create_inst_br_coord_from_csv(csv_reader)

        else:
            return {constants.STR_MESSAGE: messages.REQUEST_EMPTY_FILE_ERROR, constants.STR_ERROR: True}


# TEST
if __name__ == "__main__":
    import datetime
    from school_manager.db import initialize_db
    initialize_db.init_db()
    print(datetime.datetime.now())
    file_path = "D:\Drive\Projects\Jacob\school manager - shared\csv to index\institutions_branches_trend_coordinators.csv"
    with open(file_path, encoding=UT8_WITH_BOM_ENCODING) as csv_f:
            csv_reader_ = csv.DictReader(csv_f)
            create_inst_br_coord_from_csv(csv_reader_)
    print(datetime.datetime.now())


