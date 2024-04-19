from pydantic import BaseModel
from typing import Any


class UpdateData(BaseModel):
    data_id: int
    column: str
    new_value: Any


class CreateColumn(BaseModel):
    column_name: str
    column_type: str
