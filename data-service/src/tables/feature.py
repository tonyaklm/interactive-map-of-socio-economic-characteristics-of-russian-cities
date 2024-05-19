from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import PrimaryKeyConstraint, Index, ARRAY, Integer, Column

from db import Base
from typing import List


class FeatureDao(Base):
    __tablename__ = 'feature'
    indicator_type: Mapped[str] = mapped_column(nullable=False, primary_key=True)
    is_drawable: Mapped[bool] = mapped_column(nullable=False, default=False)
    years = Column(ARRAY(Integer), nullable=False, default=[])
    min_value: Mapped[float] = mapped_column(nullable=True)
    max_value: Mapped[float] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(nullable=True)
    agg_function: Mapped[str] = mapped_column(nullable=False, default="avg")

    __table_args__ = (
        Index('indicator_type_index' 'indicator_type'),
        Index('drawable_index' 'is_drawable'),
    )
