import os
import tempfile
from itertools import count
from pathlib import Path

# must be set before app.config is imported, so tests never touch the real database.
# TEST_DATABASE_URL runs the suite against PostgreSQL instead; that database is wiped.
os.environ["DATABASE_URL"] = os.getenv("TEST_DATABASE_URL") or f"sqlite:///{Path(tempfile.mkdtemp()) / 'test.db'}"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.db import models as db_models  # noqa: E402, F401  (registers the tables on Base)
from app.db.session import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.repositories import clinician_repo  # noqa: E402
from app.services import auth_service  # noqa: E402

PASSWORD = "correct-horse"
_ids = count(1)


@pytest.fixture(scope="session")
def client():
    # start empty: a reused PostgreSQL test database would still hold last run's clinicians
    Base.metadata.drop_all(engine)
    # "with" runs the lifespan, so the real models in models/ are loaded and tables created
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