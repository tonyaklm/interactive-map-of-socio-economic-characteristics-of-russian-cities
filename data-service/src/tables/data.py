from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import PrimaryKeyConstraint
from db import Base


class DataDao(Base):
    __tablename__ = 'data'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    region_id: Mapped[int] = mapped_column(nullable=False)
    region: Mapped[str] = mapped_column(nullable=False)
    municipality: Mapped[str] = mapped_column(nullable=False)
    settlement: Mapped[str] = mapped_column(nullable=False)
    type: Mapped[str] = mapped_column(nullable=False)
    population: Mapped[int] = mapped_column(nullable=False)
    children: Mapped[int] = mapped_column(nullable=False)
    latitude_dms: Mapped[str] = mapped_column(nullable=False)
    longitude_dms: Mapped[str] = mapped_column(nullable=False)
    latitude_dd: Mapped[float] = mapped_column(nullable=False)
    longitude_dd: Mapped[float] = mapped_column(nullable=False)
    oktmo: Mapped[float] = mapped_column(nullable=False)
    dadata: Mapped[int] = mapped_column(nullable=False)
    rosstat: Mapped[int] = mapped_column(nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('id', name='municipality_pkey'),
    )
