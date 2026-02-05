from school_manager.db import db, init_db_schema
import pandas as pd

GET_TRIGGER_QUERY = "SHOW TRIGGERS"


def get_triggers():
    update_trigger = db.session.execute(GET_TRIGGER_QUERY)
    return [trigger['Trigger'] for trigger in [dict(row) for row in update_trigger]]


def create_expense_triggers(triggers=None):
    from school_manager.models.expense import TRIGGER_NAME, UPDATE_TRIGGER_QUERY
    if not triggers:
        update_trigger = db.session.execute(GET_TRIGGER_QUERY)
        triggers = [trigger['Trigger'] for trigger in [dict(row) for row in update_trigger]]
    if TRIGGER_NAME not in triggers:
        db.session.execute(UPDATE_TRIGGER_QUERY)


def create_periodic_reception_triggers(triggers=None):
    from school_manager.models.periodic_reception import TRIGGER_NAME, UPDATE_TRIGGER_QUERY
    if not triggers:
        update_trigger = db.session.execute(GET_TRIGGER_QUERY)
        triggers = [trigger['Trigger'] for trigger in [dict(row) for row in update_trigger]]
    if TRIGGER_NAME not in triggers:
        db.session.execute(UPDATE_TRIGGER_QUERY)


def create_default_income_source_records():
    from school_manager.models.income_source import IncomeSource, DEFAULT_CURRENT_ACCOUNT_IS, \
        DEFAULT_CLEARING_ACCOUNT_IS, DEFAULT_DONATOR_IS
    default_is = IncomeSource.read(name=DEFAULT_CURRENT_ACCOUNT_IS.get('name', ''))
    default_clearing = IncomeSource.read(name=DEFAULT_CLEARING_ACCOUNT_IS.get('name', ''))
    default_donator = IncomeSource.read(name=DEFAULT_DONATOR_IS.get('name', ''))
    if not default_is:
        IncomeSource.create(DEFAULT_CURRENT_ACCOUNT_IS)
    if not default_clearing:
        IncomeSource.create(DEFAULT_CLEARING_ACCOUNT_IS)
    if not default_donator:
        IncomeSource.create(DEFAULT_DONATOR_IS)


def create_default_trend_coordinator_records():
    from school_manager.models.trend_coordinator import TrendCoordinator, DEFAULT_TREND_COORDINATOR
    default_tc = TrendCoordinator.read(name=DEFAULT_TREND_COORDINATOR.get('name', ''))
    if not default_tc:
        TrendCoordinator.create(DEFAULT_TREND_COORDINATOR)

def create_default_parameters_records():
    from school_manager.models.parameter import Parameter, DEFAULT_PARAMETERS
    for param_name, param_value in DEFAULT_PARAMETERS.items():
        default_param = Parameter.read(name=param_name)
        if not default_param:
            Parameter.create(param_value.get('record'))

def init_db():
    # noinspection PyUnresolvedReferences
    import school_manager.models
    # Init DB empty tables
    db.Base.metadata.create_all(bind=db.engine)
    init_db_schema.init_db_schema(db)

    # add default income source for auto current account link
    create_default_income_source_records()

    # add default trend coordinator
    create_default_trend_coordinator_records()

    # add default trend coordinator
    create_default_parameters_records()

    triggers = get_triggers()
    # add triggers to update update_date field in expense model
    create_expense_triggers(triggers)
    # add triggers to update update_date field in periodic_reception model
    create_expense_triggers(triggers)
