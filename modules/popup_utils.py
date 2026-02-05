from core import messages


def get_popup_record(cls, num_of_records, success_records, errors, name='', title =''):
    if cls is not None:
        name = cls.__tablename__
        title = cls.__classnameheb__
    success_message = messages.UPLOAD_POP_UP_SUCCESS_MESSAGE.format(success_records,
                                                                    num_of_records, name)
    return dict(name=name, title=title, success=success_message, errors=errors)

def update_popup_record(cls, num_of_records, success_records, errors, name='', title =''):
    if cls is not None:
        name = cls.__tablename__
        title = cls.__classnameheb__
    success_message = messages.UPLOAD_POP_UP_SUCCESS_MESSAGE.format(success_records,
                                                                    num_of_records, name)
    return dict(name=name, title=f'עדכון {title}', success=success_message, errors=errors)

def validate_mandatory_columns(row, mandatory_columns):
    from school_manager.modules import exceptions
    row_keys = list(row.keys())
    if not all(man_col in row_keys for man_col in mandatory_columns):
        raise exceptions.UploadMandatoryColumnNotFound(mandatory_columns)