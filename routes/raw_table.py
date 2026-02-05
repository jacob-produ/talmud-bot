from flask import request, jsonify, Response
from flask_restful import Resource
from school_manager.routes.auth import login_required, role_required
from school_manager.db import db
from core import utils, date_utils
from datetime import datetime
import pandas as pd, os, inspect
from sqlalchemy.sql import func

from school_manager.models.student import Student
from school_manager.models.employee import Employee
from school_manager.models.supplier import Supplier

TABLES_QUERY = "SHOW TABLES"
DIR_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_EXPORT_PATH = os.path.join(DIR_PATH,'assets/raw_tables')
MODELS_PATH = os.path.join(DIR_PATH,'models/')

def get_db_tables():
    db_tables = [table[0] for table in db.session.execute(TABLES_QUERY)]
    return db_tables

def table_name_to_class(table_name):
    table_name_list = [name.capitalize() for name in table_name.split("_")]
    return ''.join(table_name_list)

def get_attributions_df():
    student_query = db.session.query(Student.id.label('attribution_id'), Student.identity.label('attribution_identity'),
                                        func.concat(Student.first_name, " ", Student.last_name)
                                        .label("attribution_full_name"))
    employee_query = db.session.query(Employee.id.label('attribution_id'), Employee.identity.label('attribution_identity'),
                                        func.concat(Employee.first_name, " ", Employee.last_name)
                                        .label("attribution_full_name"))
    supplier_query =  db.session.query(Supplier.id.label('attribution_id'),
                                             Supplier.identity.label('attribution_identity'), Supplier.name.label("attribution_full_name"))

    student_df = pd.read_sql(student_query.statement, db.engine)
    employee_df = pd.read_sql(employee_query.statement, db.engine)
    supplier_df = pd.read_sql(supplier_query.statement, db.engine)


    student_df['attribution'] = 'student'
    employee_df['attribution'] = 'employee'
    supplier_df['attribution'] = 'supplier'
    attribution_df = pd.concat([student_df,employee_df,supplier_df], axis=0)
    return attribution_df


def get_table_df(table_name, start_date, end_date, date_attribute):
    models_paths = utils.get_python_file_from_dir(MODELS_PATH)
    main_table_class = utils.import_class_from_file([(table_name_to_class(table_name),f'school_manager.models.{table_name}')])[0]
    foreign_keys_attributes = [attribute[0] for attribute in inspect.getmembers(main_table_class) if 'fk' in attribute[0]]
    models = [main_table_class]
    joins = []
    for key in foreign_keys_attributes:
        key_split = key.split("_")[1:-1]
        joined_table_name = '_'.join(key_split)
        joined_table_class = utils.import_class_from_file([(table_name_to_class(joined_table_name),f'school_manager.models.{joined_table_name}')])[0]
        joins.append((main_table_class, joined_table_class, key, 'id'))
        models.append(joined_table_class)

    query = db.session.query(*models)
    for join_args in joins:
        query = query.outerjoin(join_args[1],getattr(join_args[0],join_args[2]) == getattr(join_args[1],join_args[3]))
    query = query.filter(
    getattr(main_table_class,date_attribute) >= start_date,
    getattr(main_table_class,date_attribute) <= end_date)
    table_df = pd.read_sql(query.statement, db.engine)
    if 'attribution' in table_df.columns and 'attribution_id' in table_df.columns:
        table_df = table_df.merge(get_attributions_df(), how='left', on=['attribution','attribution_id'])
        print(table_df.columns)
    return table_df

def get_tables_excel(request_tables, start_date, end_date, dates_attributes):
    not_found_tables = []
    df_list, sheet_list = [], []
    db_tables =  get_db_tables()
    current_time = date_utils.get_formatted_now_date()
    excel_file_name = os.path.join(DEFAULT_EXPORT_PATH,f'tables_{current_time}.xlsx')
    zip_file_name = os.path.join(DEFAULT_EXPORT_PATH, f'tables_{current_time}.zip')
    log_file_name = os.path.join(DEFAULT_EXPORT_PATH, f'tables_{current_time}.txt')

    for table_name,date_attribute in zip(request_tables, dates_attributes):
        if table_name not in db_tables:
            not_found_tables.append(table_name)
            continue
        table_df = get_table_df(table_name, start_date, end_date,date_attribute)
        df_list.append(table_df)
        sheet_list.append(table_name)

    utils.dfs_to_excel(df_list,sheet_list, file_name=excel_file_name)
    utils.write_to_file(log_file_name, not_found_tables,prefix='all tables exported' if not not_found_tables else 'these tables does not exists')
    zip_data = utils.compress_files_to_zip([excel_file_name,log_file_name],zip_file_name=zip_file_name)
    return zip_data, os.path.basename(zip_file_name)

class RawTableAPI(Resource):
    @staticmethod
    @login_required()
    def post():
        request_body = request.get_json()
        request_tables = request_body.get('tables')
        dates_attributes = request_body.get('dates_attributes')
        start_date = datetime.strptime(request_body.get('start_date'),"%d/%m/%Y")
        end_date = datetime.strptime(request_body.get('end_date'),"%d/%m/%Y")
        zip_data, zip_file_name = get_tables_excel(request_tables, start_date, end_date,dates_attributes)

        return Response(zip_data, headers={
            'Content-Type': 'application/zip',
            'Content-Disposition': 'attachment; filename=%s;' % zip_file_name
        })

