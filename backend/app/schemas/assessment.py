from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AssessmentCreate(BaseModel):
    patient_id: int
    model_version: str
    # one key per feature in the model's metadata; None = not measured (optional features only)
    inputs: dict[str, float | None]


class Contribution(BaseModel):
    feature: str
    value: float | None
    contribution: float


class AssessmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    model_version: str
    inputs: dict[str, float | None]
    risk_probability: float
    risk_level: str
    shap_values: list[Contribution]
    created_at: datetime