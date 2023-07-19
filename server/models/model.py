import datetime
from sqlalchemy_utils.models import generic_repr
from sqlalchemy import Column, Integer, String, JSON, DateTime

from .base import Base, session_scope

@generic_repr(
    "id", "alias", "endpoint", "model_path", "model_type", "db", "deployment", "schema",
      "create_time", "update_time", "online_time")
class ModelSetting(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    alias = Column(String(128), primary_key=True, nullable=False)
    endpoint = Column(String(128), nullable=False)
    model_path = Column(String(128), nullable=False)
    model_type = Column(String(32), nullable=False)
    database = Column(String(32), nullable=False)
    deployment = Column(String(32), nullable=False)
    schema = Column(JSON, nullable=False)
    port = Column(String(128), nullable=False)
    create_time = Column(
        DateTime, nullable=False,
        default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    update_time = Column(DateTime)
    online_time = Column(DateTime)

    __tablename__ = "modelsetting"

    def __init__(self, *args, **kwargs):
        super(ModelSetting, self).__init__(*args, **kwargs)
    
    def to_dict(self):
        return {
            "id": self.id,
            "alias": self.alias,
            "endpoint": self.endpoint,
            "model_path": self.model_path,
            "model_type": self.model_type,
            "database": self.database,
            "deployment": self.deployment,
            "schema": self.schema,
            "port": self.port,
            "create_time": self.create_time,
            "update_time": self.update_time,
            "online_time": self.online_time
        }
    
    @classmethod
    def get_by_id(cls, id):
        with session_scope() as session:
            return session.query(cls).filter(cls.id == id).one()
    
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
    def get_by_endpoint(cls, db, deployment, page, size):
        with session_scope() as session:
            return session.query(cls).filter(cls.db == db, cls.deployment == deployment).limit(
                size).offset(size * (page - 1))
    