from school_manager.db import db
from marshmallow import RAISE, ValidationError
from sqlalchemy.exc import IntegrityError
from core import messages
from school_manager.constants import constants
import pandas as pd
import re

class BaseMixin:
    @classmethod
    def create(cls, object_data, with_commit=True, many=False, ignore = ''):
        # Load user input to SqlAlchemy object using marshmallow schema (for validation)
        try:
            object_to_create = cls.Schema(many=many).load(object_data, partial=False, unknown=RAISE)
        except ValidationError as err:
            return {constants.STR_MESSAGE: err.messages, constants.STR_DATA: {}, constants.STR_ERROR: True}

        # Create object
        if not many:
            db.session.add(object_to_create)
        else:
            for obj in object_to_create:
                db.session.add(obj)

        if with_commit:
            try:
                db.session.commit()
                return {constants.STR_MESSAGE: messages.CREATE_SUCCESS.format(cls.__name__),
                        constants.STR_DATA: cls.Schema().dump(object_to_create), constants.STR_ERROR: False}
            except Exception as err:
                #Integrity error
                db.session.rollback()
                err_message = re.split("[()]",err.args[0])
                message = err_message[-2] if len(err_message[-2]) > 3 else f'{err_message[3]} {err_message[5]}'
                return {constants.STR_MESSAGE: message, constants.STR_DATA: {}, constants.STR_ERROR: True}


    @classmethod
    def get_records_errors(cls,object_data,result_pd,create=True,num_modified_rows=0):
        # convert datetime to str
        if create:
            for col in result_pd.columns:
                if result_pd[col].dtype == 'datetime64[ns]':
                    result_pd[col] = result_pd[col].dt.strftime('%Y-%m-%dT%H:%M:%S')

        errored_records, headers = [], list(result_pd.columns.values)
        if type(object_data) == dict: object_data = [object_data]
        for obj in object_data:
            error = True if create else False
            for _, row in result_pd.iterrows():
                if all([str(row[i]) == str(obj[i]) for i in headers]):
                    error = False if create else True
                    break
            if error:
                errored_record = cls.create(obj) if create else cls.delete(id=obj['id'])
                del errored_record["error"]
                del errored_record["data"]
                errored_record["object"] = obj
                errored_records.append(errored_record)

        message = messages.MULTIPLE_CREATE_ERRORS if create else messages.MULTIPLE_DELETE_ERRORS
        if len(errored_records) > 0:
            return {
                constants.STR_MESSAGE: {constants.STR_VALUE: message.format(num_modified_rows, len(object_data))},
                constants.STR_DATA: errored_records, constants.STR_ERROR: True}
        message = messages.CREATE_SUCCESS if create else messages.DELETE_SUCCESS
        return {constants.STR_MESSAGE: {
            constants.STR_VALUE: message.format(cls.__tablename__)},
            constants.STR_DATA: None, constants.STR_ERROR: False}

    @classmethod
    def create_ignore(cls,object_data ,with_commit=True ,unique=[]):
        if not object_data:
            return {constants.STR_MESSAGE: {constants.STR_VALUE: messages.CREATE_NO_DATA}, constants.STR_ERROR: True}

        # try:
        #     object_to_create = cls.Schema(many=True).load(object_data, partial=False, unknown=RAISE)
        # except ValidationError as err:
        #     return {constants.STR_MESSAGE: err.messages, constants.STR_DATA: {}, constants.STR_ERROR: True}


        object_to_create = cls.__table__.insert().prefix_with('IGNORE').values(object_data)

        # for obj in object_to_create:
        result_proxy = db.session.execute(object_to_create)
        if with_commit:
            db.session.commit()
        if result_proxy and result_proxy.rowcount == len(object_data):
            return {
                constants.STR_MESSAGE: {
                constants.STR_VALUE: messages.CREATE_SUCCESS.format(cls.__tablename__)},
                constants.STR_DATA: None, constants.STR_ERROR: False
            }

        elif result_proxy and result_proxy.rowcount != len(object_data):
            if unique:
                unique_cols = unique
            else:
                try:
                    unique_cols = cls.__table_args__[0].columns
                except Exception as e:
                    unique_cols = [getattr(cls, attribute) for attribute in object_data[0].keys()]

            create_result = db.session.query(*unique_cols).order_by(cls.id.desc()).limit(result_proxy.rowcount)

            result_query = pd.read_sql(create_result.statement, db.engine)

            return cls.get_records_errors(object_data,result_query,create=True,num_modified_rows=result_proxy.rowcount)

        return {constants.STR_MESSAGE: {constants.STR_VALUE: messages.SERVER_ERROR},constants.STR_ERROR: True}

    @classmethod
    def read(cls, only_columns_list=[], exclude_columns_list=[], many=True,**filter_kw):
        if filter_kw:
            validate_dict = cls.Schema().validate(filter_kw, partial=True)
            # Checks if the validation return dict with some errors. if not parameters are valid
            if validate_dict:
                return validate_dict

            query_result = cls.query.filter_by(**filter_kw)
            if not many:
                query_result = query_result.first()

        else:
            query_result = cls.query.all()

        if only_columns_list:
            result = cls.Schema(many=many, only=only_columns_list, exclude=exclude_columns_list).dump(query_result)
        else:
            result = cls.Schema(many=many, exclude=exclude_columns_list).dump(query_result)
        db.session.commit()
        return result

    @classmethod
    def update(cls, updated_values_dict, **filter_kw):
        # Load user input to SqlAlchemy using marshmallow schema
        # partial: great for update. unknown: great for update & create
        # Use instance parameter to update the relevant db row
        if "id" in updated_values_dict:
            del updated_values_dict["id"]
        try:
            updated_object = cls().query.filter_by(**filter_kw).first()

            if not updated_object:
                return {constants.STR_MESSAGE: {constants.STR_VALUE: messages.NO_UPDATE_PERFORMED.format
                (filter_kw, cls.__name__)}, constants.STR_DATA: None, constants.STR_ERROR: True}

            updated_object_result = cls.Schema().load(updated_values_dict, instance=updated_object,
                                                      partial=True, unknown=RAISE)
        except ValidationError as err:
            return {constants.STR_MESSAGE: err.messages, constants.STR_DATA: None, constants.STR_ERROR: True}

        db.session.commit()
        return {constants.STR_MESSAGE: messages.UPDATE_SUCCESS.format(cls.__name__),
                constants.STR_DATA: cls.Schema().dump(updated_object_result), constants.STR_ERROR: False}

    @classmethod
    def delete(cls, **kw):
        result = cls.query.filter_by(**kw).delete()
        db.session.commit()

        if result == 0:
            return {constants.STR_MESSAGE: messages.DELETE_FAIL.format(cls.__name__), constants.STR_ERROR: True}

        return {constants.STR_MESSAGE: messages.DELETE_SUCCESS.format(cls.__name__), constants.STR_ERROR: False}

    @classmethod
    def delete_ignore(cls,ids,with_commit=True):
        object_to_remove = cls.__table__.delete().prefix_with('IGNORE').where(cls.id.in_(tuple(ids)))

        result_proxy = db.session.execute(object_to_remove)
        if with_commit:
            db.session.commit()
        if result_proxy and result_proxy.rowcount == len(ids):
            return {
                constants.STR_MESSAGE: {
                    constants.STR_VALUE: messages.DELETE_SUCCESS.format(cls.__tablename__)},
                constants.STR_DATA: None, constants.STR_ERROR: False
            }

        elif result_proxy and result_proxy.rowcount != len(ids):
            delete_result = db.session.query(cls.id).filter(cls.id.in_(tuple(ids)))
            result = pd.read_sql(delete_result.statement, db.engine)
            if result.shape[0] == 0:
                return {constants.STR_MESSAGE: {
                    constants.STR_VALUE: messages.DELETE_SUCCESS.format(cls.__tablename__)},
                    constants.STR_DATA: None, constants.STR_ERROR: False}

            ids = [{'id':id} for id in ids]
            return cls.get_records_errors(ids, result, create=False,
                                          num_modified_rows=result_proxy.rowcount)

        return {constants.STR_MESSAGE: {constants.STR_VALUE: messages.SERVER_ERROR}, constants.STR_ERROR: True}

    @classmethod
    def col_name(cls, col):
        return str(col).split('.')[1]
