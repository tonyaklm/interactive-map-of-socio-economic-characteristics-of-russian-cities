from sqlalchemy.ext.asyncio import create_async_engine
import sqlalchemy.orm
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from config import settings
from sqlalchemy.pool import NullPool

engine = create_async_engine(settings.database_url, echo=True, future=True, poolclass=NullPool)
Base = sqlalchemy.orm.declarative_base()
async_session = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)