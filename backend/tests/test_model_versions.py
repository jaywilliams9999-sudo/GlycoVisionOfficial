"""Newest version of each model is used for new assessments; older ones stay readable."""
from app.db.session import SessionLocal
from app.ml.registry import latest_by_family
from app.repositories import assessment_repo

from tests.test_api import CLINICAL


def test_latest_by_family_compares_version_numbers_not_text():
    versions = ["clinical-v9", "clinical-v10", "screening-v1"]
    # as text, "v9" > "v10"; as numbers, 10 wins
    assert latest_by_family(versions) == {"clinical": "clinical-v10", "screening": "screening-v1"}


def test_models_list_marks_only_the_newest_version_active(client):
    models = {m["model_version"]: m for m in client.get("/models").json()}
    assert models["clinical-v2"]["active"] is True and models["clinical-v2"]["replaced_by"] is None
    assert models["clinical-v1"]["active"] is False and models["clinical-v1"]["replaced_by"] == "clinical-v2"
    assert models["screening-v1"]["replaced_by"] == "screening-v2"


def test_new_assessments_on_a_replaced_model_are_refused(client, auth, patient_id):
    response = client.post("/assessments", json={"patient_id": patient_id, "model_version": "clinical-v1", "inputs": CLINICAL}, headers=auth)
    assert response.status_code == 410
    assert "clinical-v2" in response.json()["detail"]


def test_saved_results_from_a_replaced_model_stay_readable(client, auth, patient_id):
    # a result saved back when v1 was current, keeping v1's label
    with SessionLocal() as db:
        old = assessment_repo.create(
            db, patient_id=patient_id, model_version="clinical-v1", inputs=CLINICAL,
            shap_values=[], risk_probability=0.3, risk_level="low",
        )
    assert client.get(f"/assessments/{old.id}", headers=auth).json()["risk_level"] == "low"
    timeline = client.get(f"/patients/{patient_id}/assessments", headers=auth).json()
    assert [a["model_version"] for a in timeline] == ["clinical-v1"]
