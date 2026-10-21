from pydantic import BaseModel


class InputSpec(BaseModel):
    min: float
    max: float
    optional: bool = False


class ModelOut(BaseModel):
    model_version: str
    features: list[str]
    inputs: dict[str, InputSpec]
    metrics: dict[str, float]