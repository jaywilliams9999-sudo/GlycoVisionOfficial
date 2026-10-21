from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.auth import LoginRequest, TokenOut
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenOut)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """401 for a wrong username or password, 423 once the account is locked."""
    clinician = auth_service.authenticate(db, body.username, body.password)
    return TokenOut(access_token=auth_service.create_token(clinician), user=clinician)