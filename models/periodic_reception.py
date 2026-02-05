from core.date_utils import ISO_FORMAT

from school_manager.db import db
from school_manager.models.crud_mixin import BaseMixin
from datetime import datetime
from school_manager.constants.constants_lists import PERIODIC_RECEPTION_STATUS, EXPENSE_PAYMENT_STATUS

from school_manager.constants.constants_lists import UPLOAD_SOURCES

TRIGGER_NAME = 'periodic_reception_update_up_date'
UPDATE_TRIGGER_QUERY = f'''
            CREATE TRIGGER {TRIGGER_NAME} BEFORE UPDATE ON periodic_reception
            FOR EACH ROW
            BEGIN
                SET NEW.update_date = CONVERT_TZ (NOW(), 'SYSTEM','+03:00');
            END
        '''

ACTIVE_STATUS = PERIODIC_RECEPTION_STATUS[0]
WAITING_FOR_PERMISSION_STATUS = PERIODIC_RECEPTION_STATUS[1]
FINISHED_STATUS = PERIODIC_RECEPTION_STATUS[4]

DRAFT_EXPENSE_STATUS = EXPENSE_PAYMENT_STATUS[0]


class PeriodicReception(BaseMixin, db.Base):
    __tablename__ = "periodic_reception"
    __classnameheb__ = "תשלום מחזורי"
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    charges = db.Column(db.Integer, nullable=False)
    current_charges = db.Column(db.Integer, default=0)
    first_charge_date = db.Column(db.DateTime, nullable=False)
    last_charge_date = db.Column(db.DateTime, nullable=True)
    charge_date = db.Column(db.Integer, nullable=False)
    periodic_reception_status = db.Column(db.String(45), default=WAITING_FOR_PERMISSION_STATUS)
    payment_method = db.Column(db.String(45))
    created_date = db.Column(db.DateTime, default=datetime.now, nullable=False)
    update_date = db.Column(db.DateTime, default=datetime.now, nullable=False)
    active = db.Column(db.Boolean, default=False)
    suspend_start_date = db.Column(db.DateTime)
    suspend_end_date = db.Column(db.DateTime)
    comment = db.Column(db.String(120))

    bank_permission_start_date = db.Column(db.DateTime)
    bank_permission_end_date = db.Column(db.DateTime)
    bank_permission_applicant = db.Column(db.String(45))
    bank_permission_application_date = db.Column(db.DateTime)
    bank_permission_amount_limit = db.Column(db.Float)
    bank_permission_charge_date = db.Column(db.DateTime)

    data_source = db.Column(db.String(20), default=UPLOAD_SOURCES[0])
    data_upload_date = db.Column(db.DateTime, default=datetime.now)

    fk_donator_id = db.Column(db.Integer, db.ForeignKey('donator.id'), nullable=False)
    fk_institution_id = db.Column(db.Integer, db.ForeignKey('institution.id'), nullable=False)
    fk_trend_coordinator_id = db.Column(db.Integer, db.ForeignKey('trend_coordinator.id'), nullable=False)
    fk_student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    fk_bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_account.id'), nullable=False)

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                {i: self.__dict__[i] for i in self.__dict__ if i != "_sa_instance_state"})

    @classmethod
    def update_to_inactive(cls, ids=[]):
        for id in ids:
            cls.update(dict(active=0, periodic_reception_status=FINISHED_STATUS), id=id)

    @classmethod
    def update_created_reception(cls, receptions=[]):
        for reception in receptions:
            cls.update(reception, id=reception.get('id'))

    @classmethod
    def get_periodic_reception_active_data(cls):
        active_receptions, inactive_receptions = [], []
        current_date = datetime.today()
        today_day = current_date.day
        data = cls.read(periodic_reception_status=ACTIVE_STATUS, charge_date=today_day)

        for record in data:
            last_charge_date = datetime.strptime(record['last_charge_date'], ISO_FORMAT)
            if (record['current_charges'] >= record['charges']) or \
                    (record['last_charge_date'] is not None and last_charge_date < current_date):
                inactive_receptions.append(record['id'])
            else:
                active_receptions.append(record)
        return active_receptions, inactive_receptions

    @classmethod
    def create_income_from_periodic_reception(cls):
        from school_manager.models.income import Income
        from school_manager.models.income_source import IncomeSource
        income_new_records = []
        active_receptions, inactive_receptions = cls.get_periodic_reception_active_data()
        current_date = datetime.now().isoformat()
        fk_income_source_id = IncomeSource.ger_donator_income_source_id()
        for reception in active_receptions:
            income = dict(method=reception['payment_method'], amount=reception['amount'],
                          fk_donator_id=reception['fk_donator_id'], fk_institution_id=reception['fk_institution_id'],
                          fk_trend_coordinator_id=reception['fk_trend_coordinator_id'],
                          fk_student_id=reception['fk_student_id'], fk_bank_account_id=reception['fk_bank_account_id'],
                          payment_status=DRAFT_EXPENSE_STATUS, for_month=current_date, deposit_date=current_date,
                          transmission_date=current_date, fk_income_source_id=fk_income_source_id)
            income_new_records.append(income)
            reception['current_charges'] += 1
            if reception['current_charges'] >= reception['charges']:
                reception['active'] = False
                reception['periodic_reception_status'] = FINISHED_STATUS

        updated_incomes = Income.create_ignore(income_new_records)
        cls.update_to_inactive(inactive_receptions)
        cls.update_created_reception(active_receptions)
