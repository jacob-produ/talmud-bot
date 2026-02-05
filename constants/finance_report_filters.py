from sqlalchemy.dialects import postgresql
from school_manager.models.income import Income
from school_manager.models.income_source import IncomeSource
from school_manager.models.expense import Expense
from school_manager.models.student import Student
from school_manager.models.course_enrollment import CourseEnrollment
from school_manager.models.trend_coordinator_attribution import TrendCoordinationAttribution
from school_manager.models.employee import Employee
from school_manager.models.supplier import Supplier
from school_manager.constants import course_types
from school_manager.constants.constants_lists import EXPENSE_PAYMENT_METHODS, EXPENSE_PAYMENT_STATUS, \
    INCOME_PAYMENT_METHODS, SCHOLARSHIP_TYPES,SCHOLARSHIP_METHODS, INCOME_SOURCE, STUDENT_IDENTITY_TYPES
from school_manager.db import db
from sqlalchemy.sql import func
from sqlalchemy import or_
from sqlalchemy.sql.expression import literal
import datetime

# TODO: GET YAKOV ANSWERS ABOUT THE QUESTIONS YOU SENT HIM REGRADING THE FILTERS
# Frontend filters
NO_SCHOLARSHIP_EXPENSE = "ללא מלגה"
NO_SCHOLARSHIP_METHOD_EXPENSE = "ללא סוג מלגה"

FE_FILTERS = [
    {"title": "תאריכים", "filters": [
        {"display_name": "תאריך יצירת הכנסה",
         "name": "income_date",
         "filter_key": "income_filters"},
        {"display_name": "תאריך יצירת הוצאה",
         "name": "expense_date",
         "filter_key": "expense_filters"},
        {"display_name": "תאריך קליטה",
         "name": "student_start_date",
         "filter_key": "student_filters"},
        {"display_name": "תאריך עזיבה",
         "name": "student_end_date",
         "filter_key": "student_filters"}
    ], "name": "date_filters"},

    {"title": "הוצאות",
     "filters": [
         {"display_name": "סטטוס תשלום",
          "name": "expense_payment_status",
          "checkboxes": [*EXPENSE_PAYMENT_STATUS]},
         {"display_name": "צורת תשלום",
          "name": "expense_payment_method",
          "checkboxes": [*EXPENSE_PAYMENT_METHODS]},
         {"display_name": "סוג מלגה",
          "name": "expense_scholarship_type",
          "checkboxes": [*SCHOLARSHIP_TYPES, NO_SCHOLARSHIP_EXPENSE]},
         {"display_name": "שיטת מלגה",
          "name": "expense_scholarship_method",
          "checkboxes": [*SCHOLARSHIP_METHODS, NO_SCHOLARSHIP_METHOD_EXPENSE]},
         # Internal Use (filters for user card)
         #     {
         #     "display_name": "סוג משתמש",
         #     "name": "attribution",
         #     "checkboxes": ["student","employee","supplier"]},
         #     {"display_name": "מזהה משתמש",
         #     "name": "attribution_id",
         #     "checkboxes": [1,2,4]},
         #     }
     ],
     "name": "expense_filters"},

    {"title": "הכנסות", "filters": [
        {"display_name": "צורת הכנסה",
         "name": "income_payment_method",
         "checkboxes": INCOME_PAYMENT_METHODS},
        {"display_name": "סוג מקור הכנסה",
         "name": "income_source",
         "checkboxes": INCOME_SOURCE},
        # Internal Use (filters for user card)
        #     {
        #     "display_name": "סוג משתמש",
        #     "name": "attribution",
        #     "checkboxes": ["student","employee","supplier"]},
        #     {"display_name": "מזהה משתמש",
        #     "name": "attribution_id",
        #     "checkboxes": [1,2,4]},
        #     }
    ], "name": "income_filters"},

    {"title": "תלמידים", "filters": [
        {"display_name": "סוג מסלול",
         "name": "student_course_type",
         "checkboxes": [*list(course_types.COURSE_TYPE_REVERSED_MAP.keys()), 'ללא סוג מסלול']},
        {"display_name": "זכאות",
         "name": "student_eligibility",
         "checkboxes": ["לא זכאי", "זכאי"]},
        {"display_name": "סוג הזדהות",
         "name": "student_identity_type",
         "checkboxes": STUDENT_IDENTITY_TYPES}
    ], "name": "student_filters"},
]

PB_FILTERS = [
    {"title": "הוצאות",
     "filters": [
         {"display_name": "צורת תשלום",
          "name": "expense_payment_method",
          "checkboxes": EXPENSE_PAYMENT_METHODS},
         {"display_name": "סוג מלגה",
          "name": "expense_scholarship_type",
          "checkboxes": [*SCHOLARSHIP_TYPES, NO_SCHOLARSHIP_EXPENSE]},
         {"display_name": "שיטת מלגה",
          "name": "expense_scholarship_method",
          "checkboxes": [*SCHOLARSHIP_METHODS, NO_SCHOLARSHIP_METHOD_EXPENSE]},
     ],
     "name": "expense_filters"},

    {"title": "תלמידים", "filters": [
        {"display_name": "סוג מסלול",
         "name": "student_course_type",
         "checkboxes": list(course_types.COURSE_TYPE_REVERSED_MAP.keys())},
        {"display_name": "זכאות",
         "name": "student_eligibility",
         "checkboxes": ["לא זכאי", "זכאי"]},
        {"display_name": "סוג הזדהות",
         "name": "student_identity_type",
         "checkboxes": STUDENT_IDENTITY_TYPES}
    ], "name": "student_filters"},
]


# Backend Filters
def get_filter_query(filter_name, checked_list):
    if filter_name == 'student_eligibility':
        if len(checked_list) == 1:
            if checked_list[0] == "זכאי":
                return TrendCoordinationAttribution.eligibility_level > 0
            elif checked_list[0] == "לא זכאי":
                return TrendCoordinationAttribution.eligibility_level == 0
        elif len(checked_list) == 2:
            return TrendCoordinationAttribution.eligibility_level >= 0

    if filter_name == 'expense_scholarship_type' and NO_SCHOLARSHIP_EXPENSE in checked_list:
        return or_(Expense.scholarship_type.in_(checked_list), Expense.scholarship_type.is_(None))
    if filter_name == 'expense_scholarship_method' and NO_SCHOLARSHIP_METHOD_EXPENSE in checked_list:
        return or_(Expense.scholarship_method.in_(checked_list), Expense.scholarship_method.is_(None))
    if filter_name == 'student_course_type' and  'ללא סוג מסלול' in checked_list:
        if 'ללא סוג מסלול' in checked_list:
            return True
        return CourseEnrollment.course_type.in_(course_types.get_course_types_converted_list(checked_list))


    switcher = {
        "expense_payment_status": Expense.payment_status.in_(checked_list),
        "expense_payment_method": Expense.payment_method.in_(checked_list),
        "expense_scholarship_type": Expense.scholarship_type.in_(checked_list),
        "expense_scholarship_method": Expense.scholarship_method.in_(checked_list),
        "income_payment_method": Income.method.in_(checked_list),
        "income_source": IncomeSource.type.in_(checked_list),
        "student_identity_type": Student.identity_type.in_(checked_list),
        "fk_student_id": Expense.fk_student_id.in_(checked_list),
        "fk_employee_id": Expense.fk_employee_id.in_(checked_list),
        "fk_supplier_id": Expense.fk_supplier_id.in_(checked_list),
    }

    if filter_name.endswith("date"):
        switcher.update({
            "expense_date": Expense.created_date.between(
                *[datetime.datetime.strptime(date, '%d/%m/%Y %H:%M') for date in checked_list]),
            "income_date": Income.created_date.between(
                *[datetime.datetime.strptime(date, '%d/%m/%Y %H:%M') for date in checked_list]),
            "student_start_date": CourseEnrollment.start_date.between(
                *[datetime.datetime.strptime(date, '%d/%m/%Y %H:%M') for date in checked_list]),
            "student_end_date": CourseEnrollment.end_date.between(
                *[datetime.datetime.strptime(date, '%d/%m/%Y %H:%M') for date in checked_list])
        })

    # Return True is the filter was not found, cause the query to ignore that missing filter
    return switcher.get(filter_name, True)




# attributions
ATTRIBUTIONS = [
    {
        'name': 'student',
        'model': Student,
        'columns': [Student.identity.label('student_identity'),
                    func.concat(Student.first_name, " ", Student.last_name).label("student_full_name")
                    ],
        'join_keys': ['fk_student_id', 'id']
    },
    {
        'name': 'course_enrollment',
        'model': CourseEnrollment,
        'columns': [CourseEnrollment.id.label('course_enrollment_id')],
                    # CourseEnrollment.fk_trend_coordinator_id.label('fk_trend_coordinator_id_ce'),CourseEnrollment.payment_method.label("student_payment_method")],
        'join_keys': ['fk_course_enrollment_id', 'id']
    },
    {
        'name': 'trend_coordinator_attribution',
        'model': TrendCoordinationAttribution,
        'columns': [TrendCoordinationAttribution.fk_trend_coordinator_id.label('fk_trend_coordinator_id_ce'),
                    TrendCoordinationAttribution.payment_method.label('student_payment_method')],
        'join_keys': ['fk_student_id', 'fk_student_id']
    },
    {
        'name': 'supplier',
        'model': Supplier,
        'columns': [Supplier.identity.label('supplier_identity'), Supplier.name.label("supplier_full_name"),
                    Supplier.payment_method.label('supplier_payment_method'),literal(None).label('supplier_fk_institution_id')],
        'join_keys': ['fk_supplier_id', 'id']
    },
    {
        'name': 'employee',
        'model': Employee,
        'columns': [
                    Employee.identity.label('employee_identity'),
                    func.concat(Employee.first_name, " ", Employee.last_name)
                        .label("employee_full_name"),
                    Employee.fk_institution_id.label("employee_fk_institution_id"), Employee.payment_method.label("employee_payment_method")],
        'join_keys': ['fk_employee_id', 'id']
    },
]

def get_attributions_columns():
    columns = []
    for attribution in ATTRIBUTIONS:
        columns.extend(attribution.get('columns',[]))
    return columns

def get_attributions_models():
    # models = []
    # for attribution in ATTRIBUTIONS:
    #     models.extend(attribution.get('model',[]))
    return [attribution.get('model') for attribution in ATTRIBUTIONS]


# TODO: TEST ALL FILTERS HERE
if __name__ == "__main__":
    fe_request = {
        "expense_filters": [
            {"name": "expense_payment_status",
             "checked": ["נמסר"]},
            {"name": "expense_payment_method",
             "checked": ["מזומן"],
             },
            {"name": "expense_scholarship_type",
             "checked": ["מלגת קיום"]},
            {"name": "expense_date",
             "checked": ["01/01/2018 13:45", "01/01/2021 13:45"]},
        ],
        "income_filters": [{"name": "income_payment_method",
                            "checked": ["שיק"]},
                           {"name": "income_source",
                            "checked": ["תקצוב עירוני"]},
                           {"name": "income_date",
                            "checked": ["01/01/2017 13:45", "01/01/2021 13:45"]},
                           ],

        "student_filters": [{"name": "student_identity_type",
                             "checked": ["דרכון"]},
                            {"name": "student_course_type",
                             "checked": ["בוקר"]},
                            {"name": "student_eligibility",
                             "checked": ["זכאי"]},
                            {"name": "student_start_date",
                             "checked": ["01/01/2017 13:45", "01/01/2021 13:45"]},
                            {"name": "student_end_date",
                             "checked": ["01/01/2017 13:45", "01/01/2021 13:45"]}
                            ]
    }

    print("Attribution report filter example:\n")
    print("Expense Example\n========================")
    filters = []
    for fe_filter in fe_request["expense_filters"]:
        query_filter = get_filter_query(fe_filter["name"], fe_filter["checked"])
        filters.append(query_filter)

    expense_sum = db.session.query(Expense.attribution_id, Expense.attribution,
                                   func.sum(Expense.amount).label("expense_sum")).filter(*filters). \
        group_by(Expense.attribution, Expense.attribution_id)
    for es in expense_sum:
        print(es)

    print("\nIncome Example\n========================")
    filters = []
    for fe_filter in fe_request["income_filters"]:
        query_filter = get_filter_query(fe_filter["name"], fe_filter["checked"])
        filters.append(query_filter)

    income_sum = db.session.query(Income.attribution_id, Income.attribution,
                                  func.sum(Income.amount).label("income_sum")).filter(*filters). \
        join(Income.income_source). \
        group_by(Income.attribution, Income.attribution_id)
    for inc_s in income_sum:
        print(inc_s)

    print("\nStudent Example\n========================")
    filters = []
    for fe_filter in fe_request["student_filters"]:
        query_filter = get_filter_query(fe_filter["name"], fe_filter["checked"])
        filters.append(query_filter)

    students = db.session.query(Student.id.label('attribution_id'), Student.identity,
                                func.concat(Student.first_name, " ", Student.last_name)
                                .label("full_name")).filter(*filters)
    stat = students.statement

    for student in students:
        print(student)

    print("Summary report filter example:\n")
    # One example is enough because its identical to attribution group filters
    print("Expense Example\n========================")
    filters = []
    for fe_filter in fe_request["expense_filters"]:
        query_filter = get_filter_query(fe_filter["name"], fe_filter["checked"])
        filters.append(query_filter)
    expense_sum = db.session.query(Expense.fk_institution_id, func.sum(Expense.amount).label("expense_sum")) \
        .filter(*filters).group_by(Expense.fk_institution_id)
    for es in expense_sum:
        print(es)

    # tests after adding dates
    print("\nStudent Example\n========================")
    filters = []
    for fe_filter in fe_request["student_filters"]:
        query_filter = get_filter_query(fe_filter["name"], fe_filter["checked"])
        filters.append(query_filter)

    students = db.session.query(Student.identity_type, Student.course_type, Student.eligibility_level
                                , Student.start_date, Student.end_date).filter(*filters).join
    stat = students.statement
    # print(stat.compile(dialect=postgresql.dialect(),compile_kwargs={"literal_binds": True}))

    for student in students:
        print(student)

    print("Expense Example\n========================")
    filters = []
    for fe_filter in fe_request["expense_filters"]:
        query_filter = get_filter_query(fe_filter["name"], fe_filter["checked"])
        filters.append(query_filter)
    expense_sum = db.session.query(Expense.payment_status, Expense.payment_method,
                                   Expense.scholarship_type, Expense.actual_payment_date).filter(*filters)
    for es in expense_sum:
        print(es)

    print("\nIncome Example\n========================")
    filters = []
    for fe_filter in fe_request["income_filters"]:
        query_filter = get_filter_query(fe_filter["name"], fe_filter["checked"])
        filters.append(query_filter)

    income_sum = db.session.query(Income.method, IncomeSource.type,
                                  Income.for_month).filter(*filters).join(Income.income_source)
    for inc_s in income_sum:
        print(inc_s)
