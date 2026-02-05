import types, re
from flask_login import UserMixin
from school_manager.db import db
from school_manager.models.crud_mixin import BaseMixin
from school_manager.models.branch import Branch
from school_manager.models.institution import Institution
from school_manager.models.trend_coordinator import TrendCoordinator
from school_manager.models.student_history import StudentHistory
from core import messages
from school_manager.constants import constants
from school_manager.constants.constants_lists import STUDENT_IDENTITY_TYPES

from school_manager.constants.constants_lists import UPLOAD_SOURCES
from datetime import datetime

INSTITUTION_NUMBER_CSV_COL = "מספר מוסד"
BRANCH_SYMBOL_CSV_COL = "סניף"
TREND_COORDINATOR_NAME_CSV_COL = "אחראי קבוצה"


class Student(BaseMixin, db.Base, UserMixin):
    __tablename__ = "student"
    __classnameheb__ = "סטודנטים"

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(45))
    last_name = db.Column(db.String(45))
    identity = db.Column(db.String(45), nullable=False)
    identity_type = db.Column(db.String(45), nullable=False)
    birth_date = db.Column(db.DateTime)
    main_phone_number = db.Column(db.String(20), nullable=False)
    secondary_phone_number = db.Column(db.String(20))
    state = db.Column(db.String(20))
    city = db.Column(db.String(20))
    street = db.Column(db.String(20))
    street_number = db.Column(db.String(20))
    active = db.Column(db.Boolean, default=True)
    deleted = db.Column(db.Boolean, default=False)
    marital_status = db.Column(db.String(20))
    first_parent_phone = db.Column(db.String(45))
    second_parent_phone = db.Column(db.String(45))
    home_phone = db.Column(db.String(45))
    mail = db.Column(db.String(45))
    father_name = db.Column(db.String(45))
    partner_name = db.Column(db.String(45))
    language = db.Column(db.String(45))
    entrance_country_date = db.Column(db.DateTime)
    departure_country_date = db.Column(db.DateTime)
    service_status = db.Column(db.String(20))

    data_source = db.Column(db.String(20), default=UPLOAD_SOURCES[0])
    data_upload_date = db.Column(db.DateTime, default=datetime.now)

    # Unique Constraints
    __table_args__ = (db.UniqueConstraint('identity', 'identity_type', name='_student_identity_uc'),
                      db.UniqueConstraint('main_phone_number', name='_student_phone_uc'))

    @classmethod
    def get_csv_conversion_dict(cls):
        return {
            "first_name": "שם פרטי",
            "last_name": "שם משפחה",
            "identity": "תעודת זהות",
            "identity_type": "סוג זיהוי",
            "fk_branch_id": cls.get_branch_id_from_csv_row,
            "course_type": "מסלול",
            "fk_trend_coordinator_id": cls.get_trend_coordinator_id_from_csv_row,
            "eligibility_method": "eligibility_method",
            "eligibility_min": "eligibility_min",
            "eligibility_level": "eligibility_level",
        }

    @classmethod
    def insert_csv_to_db(cls, trend_coordinator_data_conflicts, branches_data_conflicts, students, total_students,
                         number_of_conflicts):
        trend_coordinator_conflicts_info = {
            constants.STR_MESSAGE: messages.FIELD_FILTER_NOT_FOUND.format('trend_coordinator'),
            constants.STR_DATA: trend_coordinator_data_conflicts}
        branch_conflicts_info = {constants.STR_MESSAGE: messages.FIELD_FILTER_NOT_FOUND.format('branch'),
                                 constants.STR_DATA: branches_data_conflicts}

        if students.get('error'):
            insertions = [int(num) for num in re.findall('\d+', students.get('message').get('value'))]
            num_of_success = total_students - number_of_conflicts - (
                    insertions[1] - insertions[0]) if insertions else total_students - number_of_conflicts

        else:
            num_of_success = total_students - number_of_conflicts

        if num_of_success != total_students:
            return {constants.STR_MESSAGE: messages.MULTIPLE_CREATE_ERRORS.format(num_of_success, total_students),
                    constants.STR_ERROR: True, 'trend_coordinator_conflicts_info': trend_coordinator_conflicts_info,
                    'branch_conflicts_info': branch_conflicts_info,
                    'insertion_errors': students.get(constants.STR_DATA)}

        return {constants.STR_MESSAGE: messages.CREATE_SUCCESS.format('student'),
                constants.STR_ERROR: False, 'trend_coordinator_conflicts_info': trend_coordinator_conflicts_info,
                'branch_conflicts_info': branch_conflicts_info,
                'insertion_errors': students.get(constants.STR_DATA)}

    # TODO: add case to update end_date (when exists in db but not in csv)
    @classmethod
    def create_from_csv(cls, csv_reader):
        students_list = []
        trend_coordinators_data_conflicts = []
        branches_data_conflicts = []
        number_of_conflicts = 0
        for csv_row in csv_reader:
            conflict = False
            student_dict = {}
            # Convert csv_row to a student object (db row)
            for db_col, csv_col in cls.get_csv_conversion_dict().items():
                if isinstance(csv_col, str):
                    if 'eligibility' in db_col and 'method' not in db_col:
                        try:
                            student_dict[db_col] = int(csv_row[csv_col])
                        except ValueError as e:
                            student_dict[db_col] = None
                    elif 'eligibility' in db_col and len(csv_row[csv_col]) == 0:
                        student_dict[db_col] = None
                    else:
                        student_dict[db_col] = csv_row[csv_col]
                elif isinstance(csv_col, types.MethodType):
                    col_value = csv_col(csv_row)
                    if not col_value and 'branch' in db_col:
                        conflict = True
                        branches_data_conflicts.append(csv_row)
                        number_of_conflicts += 1
                    elif not col_value:
                        if not conflict: number_of_conflicts += 1
                        conflict = True
                        trend_coordinators_data_conflicts.append(csv_row)

                    student_dict[db_col] = csv_col(csv_row)
            if not conflict: students_list.append(student_dict)
        students = cls.create_ignore(students_list, with_commit=True)
        total_students = csv_reader.line_num - 1
        return cls.insert_csv_to_db(trend_coordinators_data_conflicts, branches_data_conflicts, students,
                                    total_students, number_of_conflicts)

    @classmethod
    def get_branch_id_from_csv_row(cls, csv_row):
        # TODO: Take care of case when branch not found
        institution_identity = csv_row[INSTITUTION_NUMBER_CSV_COL]
        branch_symbol = csv_row[BRANCH_SYMBOL_CSV_COL]
        branch = Branch.query.filter(Branch.symbol == branch_symbol,
                                     Branch.institution.has(Institution.identity == institution_identity)).first()
        return branch.id if branch else branch

    @classmethod
    def get_trend_coordinator_id_from_csv_row(cls, csv_row):
        return TrendCoordinator.get_trend_coordinator_by_name(name=csv_row[TREND_COORDINATOR_NAME_CSV_COL],
                                                              many=False).get('id')

    @classmethod
    def get_student_by_identity(cls, identity, identity_type=STUDENT_IDENTITY_TYPES[1]):
        return cls.read(many=False, identity=identity, identity_type=identity_type)

    @classmethod
    def create(cls, object_data, with_commit=True, many=False, ignore=''):
        try:
            identity = str(int(object_data.get('identity')))
            object_data['identity'] = identity
        except ValueError as e:
            pass
        return super(Student, cls).create(object_data=object_data, with_commit=with_commit, many=many, ignore=ignore)

    @classmethod
    def create_ignore(cls, object_data, with_commit=True, unique=[]):
        for obj in object_data:
            try:
                identity = str(int(obj.get('identity')))
                obj['identity'] = identity
            except ValueError as e:
                pass
        return super(Student, cls).create_ignore(object_data=object_data, with_commit=with_commit, unique=unique)

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                {i: self.__dict__[i] for i in self.__dict__ if i != "_sa_instance_state"})

    # using student history instead
    @classmethod
    def read(cls, only_columns_list=[], exclude_columns_list=[], many=True, **filter_kw):
        if 'identity' not in filter_kw:
            return super(Student, cls).read(only_columns_list=only_columns_list,
                                            exclude_columns_list=exclude_columns_list, many=many, **filter_kw)
        student = super(Student, cls).read(only_columns_list=only_columns_list,
                                           exclude_columns_list=exclude_columns_list, many=many, **filter_kw)
        student_history = StudentHistory.read(identity=filter_kw.get('identity'))

        if not many or len(student_history) == 1:
            return student
        student_update = [{**student, **studnet_history_instance} for studnet_history_instance in student_history]
        return student_update
