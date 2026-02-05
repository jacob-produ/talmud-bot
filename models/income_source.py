from school_manager.db import db
from school_manager.models.crud_mixin import BaseMixin

DEFAULT_CURRENT_ACCOUNT_IS = {
    'name': 'עובר ושב - זמני',
    'type': 'זמני',
    'fund_raiser': ''
}
DEFAULT_CLEARING_ACCOUNT_IS = {
    'name': 'סליקה - זמני',
    'type': 'זמני',
    'fund_raiser': ''
}

DEFAULT_DONATOR_IS = {
    'name': 'תורם - זמני',
    'type': 'זמני',
    'fund_raiser': ''
}


class IncomeSource(BaseMixin, db.Base):
    __tablename__ = "income_source"
    __classnameheb__ = "מקור הכנסה"
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=False)
    # Income source type - Tuition \ City budget \ Government budget \ Donations
    type = db.Column(db.String(45), nullable=False)
    aid_fund_allotment = db.Column(db.Integer)
    test_fund_allotment = db.Column(db.Integer)
    teaching_fund_allotment = db.Column(db.Integer)
    excellence_fund_allotment = db.Column(db.Integer)
    fund_raiser = db.Column(db.String(45))

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                {i: self.__dict__[i] for i in self.__dict__ if i != "_sa_instance_state"})

    @classmethod
    def ger_donator_income_source_id(cls):
        return cls.read(name=DEFAULT_DONATOR_IS['name'], many=False).get('id')
