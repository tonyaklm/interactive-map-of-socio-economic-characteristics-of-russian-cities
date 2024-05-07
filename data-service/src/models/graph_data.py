from pydantic import BaseModel


class UpdateGraphData(BaseModel):
    settlement: str
    longitude_dd: float
    latitude_dd: float

