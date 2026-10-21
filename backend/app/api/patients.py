from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_clinician, get_db
from app.exceptions import PatientNotFound
from app.repositories import assessment_repo, patient_repo
from app.schemas.assessment import AssessmentOut
from app.schemas.patient import PatientCreate, PatientOut

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post("", response_model=PatientOut, status_code=201)
def create_patient(body: PatientCreate, db: Session = Depends(get_db), clinician=Depends(get_current_clinician)):
    return patient_repo.create(db, clinician.id, body.identifier, body.date_of_birth)


@router.get("", response_model=list[PatientOut])
def list_patients(db: Session = Depends(get_db), clinician=Depends(get_current_clinician)):
    return patient_repo.list_all(db, clinician.id)


@router.get("/{patient_id}", response_model=PatientOut)
def get_patient(patient_id: int, db: Session = Depends(get_db), clinician=Depends(get_current_clinician)):
    patient = patient_repo.get(db, patient_id, clinician.id)
    if patient is None:
        raise PatientNotFound(patient_id)
    return patient


@router.get("/{patient_id}/assessments", response_model=list[AssessmentOut])
def list_patient_assessments(patient_id: int, db: Session = Depends(get_db), clinician=Depends(get_current_clinician)):
    """The Risk Timeline."""
    if patient_repo.get(db, patient_id, clinician.id) is None:
        raise PatientNotFound(patient_id)
    return assessment_repo.list_for_patient(db, patient_id)