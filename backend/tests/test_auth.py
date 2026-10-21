"""Login, lockout after 5 failures, and that patient data needs a valid token."""
from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app import config


def test_login_returns_token_and_name_but_no_password_hash(client, make_clinician, login):
    response = login(make_clinician())
    assert response.status_code == 200
    body = response.json()
    assert body["access_token"] and body["token_type"] == "bearer"
    assert body["user"]["name"] == "Test Clinician"
    assert "password_hash" not in str(body)


def test_wrong_password_and_unknown_user_look_the_same(client, make_clinician, login):
    wrong_password = login(make_clinician(), "nope")
    unknown_user = login("nobody", "nope")
    assert wrong_password.status_code == unknown_user.status_code == 401
    assert wrong_password.json() == unknown_user.json()


def test_fifth_failure_locks_the_account_even_for_the_right_password(client, make_clinician, login):
    username = make_clinician()
    statuses = [login(username, "nope").status_code for _ in range(config.MAX_FAILED_LOGINS)]
    assert statuses == [401, 401, 401, 401, 423]
    assert login(username).status_code == 423


def test_successful_login_resets_the_failure_count(client, make_clinician, login):
    username = make_clinician()
    for _ in range(config.MAX_FAILED_LOGINS - 1):
        login(username, "nope")
    assert login(username).status_code == 200
    assert login(username, "nope").status_code == 401  # count restarted, not locked


def test_locking_an_account_cuts_off_its_existing_token(client, make_clinician, login):
    username = make_clinician()
    headers = {"Authorization": f"Bearer {login(username).json()['access_token']}"}
    for _ in range(config.MAX_FAILED_LOGINS):
        login(username, "nope")
    assert client.get("/patients", headers=headers).status_code == 401


def _token(sub: str, minutes: int, key: str = config.SECRET_KEY) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode({"sub": sub, "iat": now, "exp": now + timedelta(minutes=minutes)}, key, algorithm="HS256")


@pytest.mark.parametrize("headers", [
    {},
    {"Authorization": "Bearer not-a-token"},
    {"Authorization": f"Bearer {_token('1', -1)}"},  # expired
    {"Authorization": f"Bearer {_token('1', 30, key='x' * 32 + 'attacker')}"},  # forged
])
def test_patient_routes_reject_missing_or_bad_tokens(client, headers):
    assert client.get("/patients", headers=headers).status_code == 401
    assert client.post("/assessments", json={}, headers=headers).status_code == 401


def test_models_list_is_public(client):
    assert client.get("/models").status_code == 200


def test_clinicians_only_see_their_own_patients(client, auth, patient_id, make_clinician, login):
    other = {"Authorization": f"Bearer {login(make_clinician()).json()['access_token']}"}
    assert client.get("/patients", headers=other).json() == []
    assert client.get(f"/patients/{patient_id}", headers=other).status_code == 404
    assert client.get(f"/patients/{patient_id}/assessments", headers=other).status_code == 404
    assert client.get(f"/patients/{patient_id}", headers=auth).status_code == 200