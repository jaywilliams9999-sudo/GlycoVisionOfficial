from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_registry
from app.exceptions import AssessmentNotFound
from app.repositories import assessment_repo
from app.schemas.assessment import AssessmentCreate, AssessmentOut
from app.services import scoring_service

router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.post("", response_model=AssessmentOut, status_code=201)
def create_assessment(body: AssessmentCreate, db: Session = Depends(get_db), registry=Depends(get_registry)):
    return scoring_service.create_assessment(db, registry, body)


@router.get("/{assessment_id}", response_model=AssessmentOut)
def get_assessment(assessment_id: int, db: Session = Depends(get_db)):
    assessment = assessment_repo.get(db, assessment_id)
    if assessment is None:
        raise AssessmentNotFound(assessment_id)
    return assessment