from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Patient


def create(db: Session, identifier: str, date_of_birth: date) -> Patient:
    patient = Patient(identifier=identifier, date_of_birth=date_of_birth)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def get(db: Session, patient_id: int) -> Patient | None:
    return db.get(Patient, patient_id)


def list_all(db: Session) -> list[Patient]:
    return list(db.scalars(select(Patient).order_by(Patient.id)))