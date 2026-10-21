from fastapi import APIRouter, Depends

from app.api.deps import get_registry
from app.schemas.model_info import ModelOut

router = APIRouter(prefix="/models", tags=["models"])


@router.get("", response_model=list[ModelOut])
def list_models(registry=Depends(get_registry)):
    """Each model's features and input ranges, so the frontend can build its form."""
    return [entry.metadata for entry in registry.values()]