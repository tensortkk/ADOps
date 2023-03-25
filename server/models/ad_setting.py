import datetime
from sqlalchemy_utils.models import generic_repr
from sqlalchemy import Column, Integer, String, JSON, DateTime

from .base import Base, session_scope


@generic_repr(
    "id", "projectName", "mode", "name", "alias",
    "setting", "create_time", "update_time", "online_time")
class ADSetting(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    projectName = Column(String(32), nullable=False)
    mode = Column(String(24), nullable=False)
    name = Column(String(128), primary_key=True, nullable=False)
    alias = Column(String(128), primary_key=True, nullable=False)
    setting = Column(JSON, nullable=False)
    create_time = Column(
        DateTime, nullable=False,
        default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    update_time = Column(DateTime)
    online_time = Column(DateTime)

    __tablename__ = "ad_setting"

    def __init__(self, *args, **kwargs):
        super(ADSetting, self).__init__(*args, **kwargs)

    def to_dict(self):
        return {
            "id": self.id,
            "mode": self.mode,
            "alias": self.alias,
            "setting": self.setting,
            "create_time": self.create_time,
            "update_time": self.update_time,
            "online_time": self.online_time
        }

    @classmethod
    def get_by_id(cls, id):
        with session_scope() as session:
            return session.query(cls).filter(cls.id == id).one()

    @classmethod
    def name_exist(cls, name):
        with session_scope() as session:
            return session.query(cls).filter(cls.name == name).count() == 1

    @classmethod
    def alias_exist(cls, alias):
        with session_scope() as session:
            return session.query(cls).filter(cls.alias == alias).count() == 1

    @classmethod
    def id_exist(cls, id):
        with session_scope() as session:
            return session.query(cls).filter(cls.id == id).count() == 1

    @classmethod
    def get_by_alias(cls, alias):
        with session_scope() as session:
            return session.query(cls).filter(cls.alias == alias).one()

    @classmethod
    def get_by_project(cls, projectName, page, page_size):
        with session_scope() as session:
            return session.query(cls).filter(cls.projectName == projectName).limit(
                page_size).offset(page_size * (page - 1))

    @classmethod
    def get_by_mode(cls, mode, page, page_size):
        with session_scope() as session:
            return session.query(cls).filter(cls.mode == mode).limit(
                page_size).offset(page_size * (page - 1))
