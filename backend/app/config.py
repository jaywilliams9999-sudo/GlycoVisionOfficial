"""Settings read from environment variables, with defaults for local development."""
import os
from pathlib import Path

# app/config.py -> parents[0]=app, [1]=backend, [2]=repo root
REPO_ROOT = Path(__file__).resolve().parents[2]

MODEL_DIR = Path(os.getenv("MODEL_DIR", REPO_ROOT / "models"))
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{REPO_ROOT / 'backend' / 'glycovision.db'}")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
