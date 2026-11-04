from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict


class EquipmentResponse(BaseModel):
    id: int
    equipment_id: str
    name: str
    category: str
    location: str

    model_config = ConfigDict(from_attributes=True)


class SensorReadingResponse(BaseModel):
    id: int
    sensor_id: int
    value: float
    recorded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AlertResponse(BaseModel):
    id: int
    reading_id: int
    severity: str
    message: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AlertStatusUpdate(BaseModel):
    status: Literal["acknowledged", "resolved"]