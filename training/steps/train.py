"""Fit the model pipeline (imputer -> random forest) on training data only."""
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline


def build_pipeline(cfg: dict) -> Pipeline:
    """The unfitted imputer + random forest pipeline described by the config."""
    return Pipeline(steps=[
        ("imputer", SimpleImputer(**cfg["impute"])),
        ("rf", RandomForestClassifier(**cfg["model"])),
    ])


def fit_model(X_train: pd.DataFrame, y_train: pd.Series, cfg: dict) -> Pipeline:
    """
    Build and fit an imputer + random forest pipeline.

    The imputer learns its medians from X_train only, and those medians are
    saved inside the pipeline, so the backend fills gaps exactly as training did.

    Args:
        X_train (pd.DataFrame): Training features (output of split()).
        y_train (pd.Series): Training labels.
        cfg (dict): The training configuration dictionary.

    Returns:
        Pipeline: Fitted pipeline with steps "imputer" and "rf".
    """
    pipeline = build_pipeline(cfg)
    pipeline.fit(X_train, y_train)
    return pipeline
