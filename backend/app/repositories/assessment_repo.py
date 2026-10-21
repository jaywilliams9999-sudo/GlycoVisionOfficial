from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Assessment


def create(db: Session, **fields) -> Assessment:
    assessment = Assessment(**fields)
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


def get(db: Session, assessment_id: int) -> Assessment | None:
    return db.get(Assessment, assessment_id)


def list_for_patient(db: Session, patient_id: int) -> list[Assessment]:
    """Oldest first, so the Risk Timeline reads left to right."""
    query = select(Assessment).where(Assessment.patient_id == patient_id).order_by(Assessment.created_at)
    return list(db.scalars(query))