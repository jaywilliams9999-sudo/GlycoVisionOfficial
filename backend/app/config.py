"""Settings read from environment variables, with defaults for local development."""
import os
from pathlib import Path

# app/config.py -> parents[0]=app, [1]=backend, [2]=repo root
REPO_ROOT = Path(__file__).resolve().parents[2]

MODEL_DIR = Path(os.getenv("MODEL_DIR", REPO_ROOT / "models"))
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{REPO_ROOT / 'backend' / 'glycovision.db'}")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

# Signs login tokens. Anyone with this key can forge a login, so set a long random
# SECRET_KEY outside development (python -c "import secrets; print(secrets.token_hex(32))").
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-secret-key-change-me-before-any-real-use")
TOKEN_MINUTES = int(os.getenv("TOKEN_MINUTES", "30"))
MAX_FAILED_LOGINS = 5