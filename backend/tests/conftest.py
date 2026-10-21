import os
import tempfile
from pathlib import Path

# must be set before app.config is imported, so tests never touch the real glycovision.db
os.environ["DATABASE_URL"] = f"sqlite:///{Path(tempfile.mkdtemp()) / 'test.db'}"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    # "with" runs the lifespan, so the real models in models/ are loaded
    with TestClient(app) as c:
        yield c


@pytest.fixture
def patient_id(client):
    response = client.post("/patients", json={"identifier": "TEST-001", "date_of_birth": "1970-01-01"})
    return response.json()["id"]