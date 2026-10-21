from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class PatientCreate(BaseModel):
    identifier: str = Field(min_length=1, max_length=64)
    date_of_birth: date


class PatientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    identifier: str
    date_of_birth: date
    created_at: datetime