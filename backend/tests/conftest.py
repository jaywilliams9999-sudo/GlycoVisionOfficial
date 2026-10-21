import os
import tempfile
from itertools import count
from pathlib import Path

# must be set before app.config is imported, so tests never touch the real glycovision.db
os.environ["DATABASE_URL"] = f"sqlite:///{Path(tempfile.mkdtemp()) / 'test.db'}"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.db.session import SessionLocal  # noqa: E402
from app.main import app  # noqa: E402
from app.repositories import clinician_repo  # noqa: E402
from app.services import auth_service  # noqa: E402

PASSWORD = "correct-horse"
_ids = count(1)


@pytest.fixture(scope="session")
def client():
    # "with" runs the lifespan, so the real models in models/ are loaded
    with TestClient(app) as c:
        yield c


@pytest.fixture
def make_clinician(client):
    """Creates a clinician with a unique username and returns the username."""
    def make() -> str:
        username = f"clinician{next(_ids)}"
        with SessionLocal() as db:
            clinician_repo.create(db, username, "Test Clinician", auth_service.hash_password(PASSWORD))
        return username
    return make


@pytest.fixture
def login(client):
    def do(username: str, password: str = PASSWORD):
        return client.post("/auth/login", json={"username": username, "password": password})
    return do


@pytest.fixture
def auth(make_clinician, login):
    """Headers for a freshly signed-in clinician."""
    return {"Authorization": f"Bearer {login(make_clinician()).json()['access_token']}"}


@pytest.fixture
def patient_id(client, auth):
    response = client.post("/patients", json={"identifier": "TEST-001", "date_of_birth": "1970-01-01"}, headers=auth)
    return response.json()["id"]