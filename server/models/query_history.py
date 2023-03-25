from sqlalchemy_utils.models import generic_repr
from sqlalchemy import Column, Integer, String, func, Text, Boolean, Float, DateTime

from .base import Base, session_scope


@generic_repr(
    "id", "ts", "user", "sql", "project", "pushdown", "runtime",
    "kylin_status_code", "error_msg")
class QueryHistory(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts = Column(DateTime, nullable=False)
    user = Column(String(32))
    sql = Column(Text)
    projectName = Column(String(32), nullable=False)
    pushdown = Column(Boolean, default=False)
    runtime = Column(Float)
    engin = Column(String(16), default="spark")
    kylin_status_code = Column(Integer)
    error_msg = Column(Text)

    __tablename__ = "kylin_metadata_query_history"

    def __init__(self, *args, **kwargs):
        super(QueryHistory, self).__init__(*args, **kwargs)

    def to_dict(self):
        return {
            "id": id,
            "ts": self.ts,
            "user": self.user,
            "sql": self.sql,
            "projectName": self.projectName,
            "pushdown": self.pushdown,
            "runtime": self.pushdown,
            "engin": self.engin,
            "kylin_status_code": self.kylin_status_code,
            "error_msg": self.error_msg
        }

    @classmethod
    def get_by_id(cls, id):
        with session_scope() as session:
            return session.query(cls).filter(cls.id == id).one()

    @classmethod
    def get_by_user(cls, user, page, page_size):
        with session_scope() as session:
            return session.query(cls).filter(cls.user == user).limit(
                page_size).offset(page_size * (page - 1))

    @classmethod
    def get_user_cnt(cls):
        with session_scope() as session:
            return session.query(cls.user, func.count(cls.user)).group_by(cls.user).all()
