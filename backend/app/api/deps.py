"""FastAPI dependencies. Tests override these to inject a fake registry or test DB."""
from fastapi import Request

from app.db.session import get_db
from app.ml.registry import ModelEntry

__all__ = ["get_db", "get_registry"]  # routes import every dependency from here


def get_registry(request: Request) -> dict[str, ModelEntry]:
    return request.app.state.registry