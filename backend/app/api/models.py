from fastapi import APIRouter, Depends

from app.api.deps import get_registry
from app.schemas.model_info import ModelOut

router = APIRouter(prefix="/models", tags=["models"])


@router.get("", response_model=list[ModelOut])
def list_models(registry=Depends(get_registry)):
    """Each model's features and input ranges, so the frontend can build its form.
    Replaced versions are listed too, so saved results can still be shown with their own cut-offs."""
    return [{**entry.metadata, "active": entry.active, "replaced_by": entry.replaced_by} for entry in registry.values()]