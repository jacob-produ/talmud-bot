from school_manager.db import db
from school_manager.models.crud_mixin import BaseMixin

DEFAULT_PARAMETERS = {
    'expense_merge_last_value': dict(record={'name': 'expense_merge_last_value', 'value': '1'}, type=int),
    'income_merge_last_value': dict(record={'name': 'income_merge_last_value', 'value': '1'}, type=int)
}


class Parameter(BaseMixin, db.Base):
    __tablename__ = "parameter"
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=False, unique=True)
    value = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                {i: self.__dict__[i] for i in self.__dict__ if i != "_sa_instance_state"})

    @classmethod
    def read_all_parameters(cls):
        parameters_dict = {}
        parameters = cls.read()
        for param_record in parameters:
            param_name, param_value = param_record.get('name'), param_record.get('value')
            if param_name in DEFAULT_PARAMETERS:
                parameters_dict[param_name] = DEFAULT_PARAMETERS[param_name]['type'](param_value)
            else:
                parameters_dict[param_name] = param_value

        return parameters_dict
