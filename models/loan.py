from school_manager.db import db
from school_manager.models.crud_mixin import BaseMixin


class Loan(BaseMixin, db.Base):
    __tablename__ = "loan"
    __classnameheb__ = "הלוואה"
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    fk_account_id = db.Column(db.Integer, db.ForeignKey('bank_account.id'), nullable=False)
    total_amount = db.Column(db.Integer, nullable=False)
    monthly_amount = db.Column(db.Integer, nullable=False)
    annual_interest = db.Column(db.Float, nullable=False)
    lender = db.Column(db.String(45), nullable=False)
    aid_fund_allotment = db.Column(db.Integer)
    test_fund_allotment = db.Column(db.Integer)
    teaching_fund_allotment = db.Column(db.Integer)
    excellence_fund_allotment = db.Column(db.Integer)

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                {i: self.__dict__[i] for i in self.__dict__ if i != "_sa_instance_state"})