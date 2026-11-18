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
    # set by load_registry: None for the newest version of its family, else the newer version
    replaced_by: str | None = None

    @property
    def active(self) -> bool:
        """Only the newest version takes new assessments; older ones stay for saved results."""
        return self.replaced_by is None


def _family_and_number(version: str) -> tuple[str, int]:
    """"clinical-v12" -> ("clinical", 12)."""
    family, _, number = version.rpartition("-v")
    if not family or not number.isdigit():
        raise RuntimeError(f"Model version {version!r} must look like <name>-v<number>.")
    return family, int(number)


def latest_by_family(versions: list[str]) -> dict[str, str]:
    """The highest-numbered version of each model family, compared as numbers (v10 > v9)."""
    latest: dict[str, str] = {}
    for version in versions:
        family, number = _family_and_number(version)
        if family not in latest or number > _family_and_number(latest[family])[1]:
            latest[family] = version
    return latest


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

    latest = latest_by_family(list(registry))
    for version, entry in registry.items():
        newest = latest[_family_and_number(version)[0]]
        entry.replaced_by = None if newest == version else newest
    return registry