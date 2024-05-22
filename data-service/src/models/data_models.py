from pydantic import BaseModel
from typing import Any


class UpdateData(BaseModel):
    matching_column_value: float
    matching_column_name: str
    column: str
    new_value: Any


class CreateColumn(BaseModel):
    column_name: str
    column_type: str


class City(BaseModel):
    settlement: str
    region: str
    region_id: int
    longitude_dd: float
    latitude_dd: float
