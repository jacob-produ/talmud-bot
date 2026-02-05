import operator
from school_manager.modules import exceptions

def percentage(num, reverse=True):
    return num / 100

def get_trend_coordinator_number_of_students(trend_coordinator_id):
    import pandas as pd
    from school_manager.db import db
    from school_manager.models.student import Student
    trend_coordinator_students_query = db.session.query(Student.identity,Student.fk_trend_coordinator_id)\
        .distinct(Student.identity,Student.fk_trend_coordinator_id).filter_by(fk_trend_coordinator_id=trend_coordinator_id)

    trend_coordinator_students_query_df = pd.read_sql(trend_coordinator_students_query.statement, db.engine)

    return trend_coordinator_students_query_df.shape[0]

ALLOTMENT_METHOD_MAP = {
    "A": {
        'funcs': [percentage, operator.mul],
        'funcs_args': [("eligibility_level",), ("calc_res", "income_amount")],
        'inverse': False
    },
    "B": {
        'funcs': [operator.sub],
        'funcs_args': [("income_amount", "eligibility_level")],
        'inverse': False
    },
    "C": {
        'funcs': [operator.sub],
        'funcs_args': [("income_amount", "eligibility_level")],
        'inverse': True
    },
    "D": {
        'funcs': [get_trend_coordinator_number_of_students,operator.floordiv, operator.sub],
        'funcs_args': [("trend_coordinator_id",),("eligibility_level", "calc_res"), ("income_amount", "calc_res")],
        'inverse': False
    },
}


def allotment_preparation(student_record):
    eligibility_method, eligibility_min, eligibility_level = student_record.get('eligibility_method'), student_record.get(
        'eligibility_min'), student_record.get('eligibility_level')
    if all([eligibility_method, eligibility_min, eligibility_level]):
        return eligibility_method, eligibility_min, float(eligibility_level), None

    from school_manager.models.trend_coordinator import TrendCoordinator
    trend_coordinator_id = student_record.get('fk_trend_coordinator_id')
    if not trend_coordinator_id:
        return None, None, None, None
    trend_coordinator_record = TrendCoordinator.read(many=False, id=trend_coordinator_id)
    if not trend_coordinator_record:
        return None, None, None, None
    eligibility_method, eligibility_min, eligibility_level = trend_coordinator_record['eligibility_method'], \
                                                             trend_coordinator_record[
                                                                 'eligibility_min'], trend_coordinator_record[
                                                                 'eligibility_level']
    if not all([eligibility_method, eligibility_min, eligibility_level]):
        return None, None, None, None
    return eligibility_method, eligibility_min,float(eligibility_level), trend_coordinator_id

def allotment_calculation(income_amount, eligibility_method, eligibility_min, eligibility_level,trend_coordinator_id):
    if not ALLOTMENT_METHOD_MAP.get(eligibility_method):
        return None,None, None, None, None
    method_operations = ALLOTMENT_METHOD_MAP.get(eligibility_method)
    for func,func_args in zip(method_operations['funcs'],method_operations['funcs_args']):
        locals_variables = locals()
        calc_res = func(*[locals_variables.get(variable_name) for variable_name in func_args])

    excellence_fund_allotment = income_amount - calc_res
    if excellence_fund_allotment < eligibility_min:
        excellence_fund_allotment = eligibility_min
    income_amount = income_amount - excellence_fund_allotment

    if  method_operations['inverse']:
        temp_excellence = excellence_fund_allotment
        excellence_fund_allotment = income_amount
        income_amount = temp_excellence

    return income_amount, excellence_fund_allotment, eligibility_method, eligibility_min, eligibility_level

def get_allotment_fund(student_record, income_amount):
    eligibility_method, eligibility_min, eligibility_level, trend_coordinator_id = allotment_preparation(student_record)
    if not eligibility_method:
        raise exceptions.ExcellenceAllotmentError('Could not find eligibility method')
    income_amount, excellence_fund_allotment, eligibility_method, eligibility_min, eligibility_level = allotment_calculation(
        float(income_amount), eligibility_method, eligibility_min, eligibility_level,trend_coordinator_id)
    if not income_amount:
        raise exceptions.ExcellenceAllotmentError('Could not update income_amount')
    return income_amount, excellence_fund_allotment, eligibility_method, eligibility_min, eligibility_level
