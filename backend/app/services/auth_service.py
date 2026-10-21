"""Passwords, login with lockout, and the signed tokens that prove a login."""
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from sqlalchemy.orm import Session

from app import config
from app.db.models import Clinician
from app.exceptions import AccountLocked, InvalidCredentials
from app.repositories import clinician_repo

# Checked against when the username doesn't exist, so a wrong username takes as long
# as a wrong password and response times don't reveal which usernames are real.
_DUMMY_HASH = bcrypt.hashpw(b"not-a-real-password", bcrypt.gensalt()).decode()


def hash_password(password: str) -> str:
    data = password.encode()
    if len(data) > 72:  # bcrypt only reads the first 72 bytes
        raise ValueError("Password must be at most 72 bytes.")
    return bcrypt.hashpw(data, bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    data = password.encode()
    return len(data) <= 72 and bcrypt.checkpw(data, password_hash.encode())


def authenticate(db: Session, username: str, password: str) -> Clinician:
    clinician = clinician_repo.get_by_username(db, username)
    if clinician is None:
        verify_password(password, _DUMMY_HASH)
        raise InvalidCredentials()
    # a locked account stays locked even with the right password, until an admin unlocks it
    if clinician.locked:
        raise AccountLocked()

    if not verify_password(password, clinician.password_hash):
        clinician.failed_logins += 1
        clinician.locked = clinician.failed_logins >= config.MAX_FAILED_LOGINS
        clinician_repo.save(db, clinician)
        if clinician.locked:
            raise AccountLocked()
        raise InvalidCredentials()

    if clinician.failed_logins:
        clinician.failed_logins = 0
        clinician_repo.save(db, clinician)
    return clinician


def create_token(clinician: Clinician) -> str:
    now = datetime.now(timezone.utc)
    claims = {"sub": str(clinician.id), "iat": now, "exp": now + timedelta(minutes=config.TOKEN_MINUTES)}
    return jwt.encode(claims, config.SECRET_KEY, algorithm="HS256")


def clinician_id_from_token(token: str) -> int | None:
    """None for a forged, malformed or expired token."""
    try:
        claims = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
        return int(claims["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        return None