"""App entry point. Run from backend/: uvicorn app.main:app --reload"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import config
from app.api import assessments, auth, models, patients
from app.db import models as db_models  # noqa: F401  (registers the tables on Base)
from app.db.session import Base, engine
from app.exceptions import (
    AccountLocked,
    AssessmentNotFound,
    InvalidCredentials,
    InvalidInputs,
    PatientNotFound,
    UnknownModelVersion,
)
from app.ml.registry import load_registry


@asynccontextmanager
async def lifespan(app: FastAPI):
    # runs before the first request: a broken model store stops the boot here
    app.state.registry = load_registry(config.MODEL_DIR)
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="GlycoVision API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=config.CORS_ORIGINS, allow_methods=["*"], allow_headers=["*"])

app.include_router(auth.router)
app.include_router(models.router)
app.include_router(patients.router)
app.include_router(assessments.router)

# domain exception -> HTTP status; services never know about HTTP
STATUS_FOR = {
    PatientNotFound: 404,
    AssessmentNotFound: 404,
    UnknownModelVersion: 404,
    InvalidInputs: 422,
    InvalidCredentials: 401,
    AccountLocked: 423,
}

# shown to the user as-is; one message for wrong username and wrong password
MESSAGE_FOR = {
    InvalidCredentials: "Username or password is incorrect.",
    AccountLocked: "Account locked. Contact an administrator.",
}


def _handler(status: int):
    def handle(request: Request, exc: Exception) -> JSONResponse:
        detail = MESSAGE_FOR.get(type(exc), f"{type(exc).__name__}: {exc}")
        return JSONResponse(status_code=status, content={"detail": detail})
    return handle


for exc_type, status in STATUS_FOR.items():
    app.add_exception_handler(exc_type, _handler(status))