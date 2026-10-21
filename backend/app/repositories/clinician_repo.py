from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Clinician


def create(db: Session, username: str, name: str, password_hash: str) -> Clinician:
    clinician = Clinician(username=username, name=name, password_hash=password_hash)
    db.add(clinician)
    db.commit()
    db.refresh(clinician)
    return clinician


def get(db: Session, clinician_id: int) -> Clinician | None:
    return db.get(Clinician, clinician_id)


def get_by_username(db: Session, username: str) -> Clinician | None:
    return db.scalar(select(Clinician).where(Clinician.username == username))


def save(db: Session, clinician: Clinician) -> None:
    """Write changes made to an already loaded clinician (failed logins, lock)."""
    db.commit()