from sqlalchemy import create_engine
import sqlalchemy.orm
from sqlalchemy.orm import sessionmaker, Session

from config import settings

engine = create_engine(settings.sqlalchemy_database_uri)
Base = sqlalchemy.orm.declarative_base()
session_maker = sessionmaker(
    engine, class_=Session, expire_on_commit=False
)

db_session = session_maker()
