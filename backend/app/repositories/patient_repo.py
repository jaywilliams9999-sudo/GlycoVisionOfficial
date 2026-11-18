from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Patient


def create(db: Session, clinician_id: int, identifier: str, date_of_birth: date) -> Patient:
    patient = Patient(clinician_id=clinician_id, identifier=identifier, date_of_birth=date_of_birth)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def get(db: Session, patient_id: int, clinician_id: int) -> Patient | None:
    """None when the patient doesn't exist or belongs to another clinician."""
    patient = db.get(Patient, patient_id)
    return patient if patient is not None and patient.clinician_id == clinician_id else None


def find_by_identifier(db: Session, clinician_id: int, identifier: str) -> Patient | None:
    """This clinician's patient with the same MRN, ignoring upper/lower case."""
    query = select(Patient).where(
        Patient.clinician_id == clinician_id,
        func.lower(Patient.identifier) == identifier.lower(),
    )
    return db.scalars(query).first()


def list_all(db: Session, clinician_id: int) -> list[Patient]:
    query = select(Patient).where(Patient.clinician_id == clinician_id).order_by(Patient.id)
    return list(db.scalars(query))