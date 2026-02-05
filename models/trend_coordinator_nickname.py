from school_manager.db import db
from school_manager.models.crud_mixin import BaseMixin


class TrendCoordinatorNickname(BaseMixin, db.Base):
    __tablename__ = "trend_coordinator_nickname"
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(45), index=True, unique=True)
    fk_trend_coordinator_id = db.Column(db.Integer, db.ForeignKey('trend_coordinator.id'))


    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                {i: self.__dict__[i] for i in self.__dict__ if i != "_sa_instance_state"})