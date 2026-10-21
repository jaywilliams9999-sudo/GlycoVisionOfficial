"""End to end: real models, temporary SQLite database."""
import pytest

CLINICAL = {
    "pregnancies": 2, "glucose": 148, "blood_pressure": 72, "skin_thickness": None,
    "insulin": None, "bmi": 33.6, "diabetes_pedigree": 0.627, "age": 50,
}
SCREENING = {
    "high_bp": 1, "high_chol": 1, "chol_check": 1, "bmi": 31, "smoker": 0, "stroke": 0,
    "heart_disease": 0, "phys_activity": 0, "fruits": 1, "veggies": 1, "heavy_alcohol": 0,
    "general_health": 4, "mental_health_days": 0, "physical_health_days": 5, "diff_walk": 1,
    "sex": 1, "age_group": 9,
}


def test_models_lists_both_with_input_ranges(client):
    models = {m["model_version"]: m for m in client.get("/models").json()}
    assert set(models) == {"clinical-v1", "screening-v1"}
    assert models["clinical-v1"]["inputs"]["insulin"]["optional"] is True


@pytest.mark.parametrize("model_version, inputs", [("clinical-v1", CLINICAL), ("screening-v1", SCREENING)])
def test_assessment_scores_explains_and_saves(client, auth, patient_id, model_version, inputs):
    response = client.post("/assessments", json={"patient_id": patient_id, "model_version": model_version, "inputs": inputs}, headers=auth)
    assert response.status_code == 201
    body = response.json()

    assert 0 <= body["risk_probability"] <= 1
    assert body["risk_level"] in {"low", "moderate", "high"}
    assert {c["feature"] for c in body["shap_values"]} == set(inputs)

    # SHAP is additive: base value + contributions must rebuild the probability
    entry = client.app.state.registry[model_version]
    base = float(entry.explainer.expected_value[1])
    total = base + sum(c["contribution"] for c in body["shap_values"])
    assert total == pytest.approx(body["risk_probability"], abs=0.01)

    assert client.get(f"/assessments/{body['id']}", headers=auth).json() == body


def test_timeline_returns_patient_assessments_oldest_first(client, auth, patient_id):
    for _ in range(2):
        client.post("/assessments", json={"patient_id": patient_id, "model_version": "clinical-v1", "inputs": CLINICAL}, headers=auth)
    timeline = client.get(f"/patients/{patient_id}/assessments", headers=auth).json()
    assert len(timeline) == 2
    assert timeline[0]["created_at"] <= timeline[1]["created_at"]


@pytest.mark.parametrize("change, message", [
    ({"glucose": 900}, "outside"),
    ({"age": None}, "age is required"),
])
def test_invalid_inputs_are_rejected(client, auth, patient_id, change, message):
    response = client.post("/assessments", json={
        "patient_id": patient_id, "model_version": "clinical-v1", "inputs": {**CLINICAL, **change},
    }, headers=auth)
    assert response.status_code == 422
    assert message in response.json()["detail"]


def test_missing_feature_is_rejected(client, auth, patient_id):
    inputs = {k: v for k, v in CLINICAL.items() if k != "bmi"}
    response = client.post("/assessments", json={"patient_id": patient_id, "model_version": "clinical-v1", "inputs": inputs}, headers=auth)
    assert response.status_code == 422


def test_unknown_patient_and_model_are_404(client, auth, patient_id):
    assert client.post("/assessments", json={"patient_id": 99999, "model_version": "clinical-v1", "inputs": CLINICAL}, headers=auth).status_code == 404
    assert client.post("/assessments", json={"patient_id": patient_id, "model_version": "nope", "inputs": CLINICAL}, headers=auth).status_code == 404
    assert client.get("/patients/99999", headers=auth).status_code == 404