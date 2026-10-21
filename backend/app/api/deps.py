"""FastAPI dependencies. Tests override these to inject a fake registry or test DB."""
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.models import Clinician
from app.db.session import get_db
from app.ml.registry import ModelEntry
from app.repositories import clinician_repo
from app.services import auth_service

__all__ = ["get_current_clinician", "get_db", "get_registry"]  # routes import every dependency from here

_bearer = HTTPBearer(auto_error=False)


def get_registry(request: Request) -> dict[str, ModelEntry]:
    return request.app.state.registry


def get_current_clinician(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> Clinician:
    """The clinician behind the request's "Authorization: Bearer <token>" header, or 401."""
    clinician_id = auth_service.clinician_id_from_token(credentials.credentials) if credentials else None
    clinician = clinician_repo.get(db, clinician_id) if clinician_id is not None else None
    # a locked account loses access straight away, not only once its token expires
    if clinician is None or clinician.locked:
        raise HTTPException(status_code=401, detail="Not signed in", headers={"WWW-Authenticate": "Bearer"})
    return clinician