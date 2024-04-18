from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import PrimaryKeyConstraint
from db import Base


class DataDao(Base):
    __tablename__ = 'data'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    __table_args__ = (
        PrimaryKeyConstraint('id', name='municipality_pkey'),
    )
