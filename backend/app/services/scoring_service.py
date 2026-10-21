"""Score, explain and persist one assessment."""
import pandas as pd
from sqlalchemy.orm import Session

from app.db.models import Assessment
from app.exceptions import InvalidInputs, PatientNotFound, UnknownModelVersion
from app.ml.explain import explain
from app.ml.registry import ModelEntry
from app.repositories import assessment_repo, patient_repo
from app.schemas.assessment import AssessmentCreate


def validate_inputs(inputs: dict[str, float | None], metadata: dict) -> None:
    """Exactly the model's features, each within its range; blanks only where optional."""
    expected = set(metadata["features"])
    if set(inputs) != expected:
        missing = sorted(expected - set(inputs))
        extra = sorted(set(inputs) - expected)
        raise InvalidInputs(f"Missing features: {missing}. Unexpected features: {extra}.")

    problems = []
    for feature, spec in metadata["inputs"].items():
        value = inputs[feature]
        if value is None:
            if not spec.get("optional", False):
                problems.append(f"{feature} is required")
        elif not spec["min"] <= value <= spec["max"]:
            problems.append(f"{feature}={value} is outside {spec['min']}-{spec['max']}")
    if problems:
        raise InvalidInputs("; ".join(problems))


def risk_level(probability: float, thresholds: dict) -> str:
    if probability >= thresholds["high"]:
        return "high"
    if probability >= thresholds["moderate"]:
        return "moderate"
    return "low"


def create_assessment(
    db: Session, registry: dict[str, ModelEntry], request: AssessmentCreate, clinician_id: int
) -> Assessment:
    entry = registry.get(request.model_version)
    if entry is None:
        raise UnknownModelVersion(request.model_version)
    if patient_repo.get(db, request.patient_id, clinician_id) is None:
        raise PatientNotFound(request.patient_id)

    metadata = entry.metadata
    validate_inputs(request.inputs, metadata)

    # build the row in metadata's feature order; None becomes NaN for the imputer
    features = metadata["features"]
    X = pd.DataFrame([[request.inputs[f] for f in features]], columns=features, dtype=float)
    probability = float(entry.model.predict_proba(X)[0, 1])

    return assessment_repo.create(
        db,
        patient_id=request.patient_id,
        model_version=request.model_version,
        inputs=request.inputs,
        shap_values=explain(entry, X),
        risk_probability=round(probability, 4),
        risk_level=risk_level(probability, metadata["risk_thresholds"]),
    )