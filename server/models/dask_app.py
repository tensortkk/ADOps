import datetime
from sqlalchemy_utils.models import generic_repr
from sqlalchemy import Column, Integer, String, DateTime, Enum

from .base import Base, session_scope


@generic_repr(
    "id", "alias", "pid", "create_time", "consume_ts", "state", "status")
class DaskApplication(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    alias = Column(String(128), primary_key=True, nullable=False)
    pid = Column(String(64))
    create_time = Column(
        DateTime, nullable=False,
        default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    consume_ts = Column(String(36), nullable=False)
    state = Column(Enum(
        "ALL", "NEW", "NEW_SAVING", "SUBMITTED", "ACCEPTED",
        "RUNNING", "FINISHED", "FAILED", "KILLED"
    ))
    status = Column(Enum("UNDEFINED", "FAILED", "SUCCEEDED", "KILLED"))

    __tablename__ = "dask_application"

    def __init__(self, *args, **kwargs):
        super(DaskApplication, self).__init__(*args, **kwargs)

    def to_dict(self):
        return {
            "id": self.id,
            "alias": self.alias,
            "pid": self.pid,
            "create_time": self.create_time,
            "consume_ts": self.consume_ts,
            "state": self.state,
            "status": self.status
        }

    @classmethod
    def get_by_id(cls, id):
        with session_scope() as session:
            return session.query(cls).filter(cls.id == id).one()

    @classmethod
    def id_exist(cls, id):
        with session_scope() as session:
            return session.query(cls).filter(cls.id == id).count() == 1

    @classmethod
    def alias_exist(cls, alias):
        with session_scope() as session:
            return session.query(cls).filter(cls.alias == alias).count() == 1
    
    @classmethod
    def get_by_alias(cls, alias):
        with session_scope() as session:
            return session.query(cls).filter(cls.alias == alias).one()
