from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import PrimaryKeyConstraint, Index
from db import Base


class DataDao(Base):
    __tablename__ = 'data'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    region_id: Mapped[int] = mapped_column(nullable=False)
    region: Mapped[str] = mapped_column(nullable=False)
    municipality: Mapped[str] = mapped_column(nullable=False)
    settlement: Mapped[str] = mapped_column(nullable=False)
    type: Mapped[str] = mapped_column(nullable=False)
    latitude_dms: Mapped[str] = mapped_column(nullable=False)
    longitude_dms: Mapped[str] = mapped_column(nullable=False)
    latitude_dd: Mapped[float] = mapped_column(nullable=False)
    longitude_dd: Mapped[float] = mapped_column(nullable=False)
    oktmo: Mapped[float] = mapped_column(nullable=False)
    dadata: Mapped[int] = mapped_column(nullable=False)
    rosstat: Mapped[int] = mapped_column(nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('id', name='municipality_pkey'),
        Index('latitude_dd_index' 'latitude_dd'),
        Index('longitude_dd_index' 'longitude_dd'),
        Index('region_id_index' 'region_id')
    )
