"""Load every model store under MODEL_DIR once, at startup."""
import json
from dataclasses import dataclass
from pathlib import Path

import joblib
import shap
import sklearn
from sklearn.pipeline import Pipeline


@dataclass
class ModelEntry:
    model: Pipeline
    explainer: shap.TreeExplainer
    metadata: dict


def load_registry(model_dir: Path) -> dict[str, ModelEntry]:
    """
    Read metadata.json + model.joblib from each subfolder and build its SHAP explainer.

    Raises instead of returning a partial registry, so the API refuses to boot
    with a broken model rather than failing in the middle of an appointment.
    """
    if not model_dir.is_dir():
        raise RuntimeError(f"MODEL_DIR {model_dir} does not exist.")

    registry = {}
    for folder in sorted(p for p in model_dir.iterdir() if p.is_dir()):
        metadata = json.loads((folder / "metadata.json").read_text())
        # joblib unpickles, which can run code: only point MODEL_DIR at stores our own training/ wrote
        model = joblib.load(folder / "model.joblib")

        if metadata["sklearn_version"] != sklearn.__version__:
            raise RuntimeError(
                f"{folder.name} was trained with scikit-learn {metadata['sklearn_version']}, "
                f"but {sklearn.__version__} is installed."
            )
        if list(model.feature_names_in_) != metadata["features"]:
            raise RuntimeError(f"{folder.name}: model features do not match metadata.json.")

        # SHAP explains the forest only, so it sees the imputer's output columns
        explainer = shap.TreeExplainer(model.named_steps["rf"])
        registry[metadata["model_version"]] = ModelEntry(model, explainer, metadata)

    if not registry:
        raise RuntimeError(f"No models found in {model_dir}.")
    return registry