"""Write the model store: model.joblib + metadata.json, the handoff to the backend."""
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import sklearn
from sklearn.pipeline import Pipeline

from steps.load import REPO_ROOT


def write_model_store(model: Pipeline, metrics: dict, cfg: dict) -> Path:
    """
    Save the fitted pipeline and its metadata to models/<model_version>/.

    The backend never imports training code; it only reads this folder.
    metadata["features"] is the column order the API must send, so it is
    checked against what the pipeline was actually fitted on before saving.

    Args:
        model (Pipeline): Fitted pipeline from fit_model().
        metrics (dict): Test-set metrics from score().
        cfg (dict): The training configuration dictionary.

    Returns:
        Path: The model store directory that was written.

    Raises ValueError if the pipeline's fitted columns differ from cfg["features"].
    """
    fitted = list(model.feature_names_in_)
    if fitted != cfg["features"]:
        raise ValueError(f"Pipeline was fitted on {fitted}, but config lists {cfg['features']}.")

    out_dir = REPO_ROOT / "models" / cfg["model_version"]
    out_dir.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, out_dir / "model.joblib")

    metadata = {
        "model_version": cfg["model_version"],
        "features": cfg["features"],
        "target": cfg["target"],
        "metrics": metrics,
        "risk_thresholds": cfg["risk_thresholds"],
        "trained_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sklearn_version": sklearn.__version__,
        "config_snapshot": cfg,
    }
    (out_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

    return out_dir