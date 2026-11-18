"""Patient rules the server enforces itself, so a client that skips the form can't break them."""
from datetime import date

import pytest


def years_ago(n: int, days: int = 0) -> str:
    today = date.today()
    try:
        d = today.replace(year=today.year - n)
    except ValueError:  # Feb 29 in a non-leap year
        d = today.replace(year=today.year - n, day=28)
    return date.fromordinal(d.toordinal() + days).isoformat()


def create(client, auth, identifier="MRN-1", dob=None):
    return client.post("/patients", json={"identifier": identifier, "date_of_birth": dob or years_ago(40)}, headers=auth)


def test_identifier_is_stored_trimmed(client, auth):
    assert create(client, auth, "  MRN-TRIM  ").json()["identifier"] == "MRN-TRIM"


def test_blank_identifier_is_rejected(client, auth):
    assert create(client, auth, "   ").status_code == 422


def test_duplicate_identifier_is_rejected_ignoring_case_and_spaces(client, auth):
    assert create(client, auth, "MRN-DUP").status_code == 201
    response = create(client, auth, " mrn-dup ")
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_same_identifier_is_allowed_for_a_different_clinician(client, make_clinician, login):
    # patients are private to each clinician; rejecting here would reveal another clinician's patient
    for _ in range(2):
        token = login(make_clinician()).json()["access_token"]
        assert create(client, {"Authorization": f"Bearer {token}"}, "MRN-SHARED").status_code == 201


@pytest.mark.parametrize("dob, message", [
    (years_ago(0, days=1), "future"),
    (years_ago(18, days=1), "18 and older"),   # 18 tomorrow
    (years_ago(121), "Check the date of birth"),
])
def test_out_of_range_birth_dates_are_rejected(client, auth, dob, message):
    response = create(client, auth, dob=dob)
    assert response.status_code == 422
    assert message in str(response.json()["detail"])


@pytest.mark.parametrize("dob", [years_ago(18), years_ago(120)])
def test_age_limits_are_inclusive(client, auth, dob):
    assert create(client, auth, f"MRN-EDGE-{dob}", dob=dob).status_code == 201