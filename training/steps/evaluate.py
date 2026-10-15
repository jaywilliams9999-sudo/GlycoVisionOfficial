"""Score a fitted pipeline on held-out test data."""
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score
from sklearn.pipeline import Pipeline


def score(model: Pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    """
    Compute test-set metrics for metadata.json.

    Only ever pass the TEST split here. Scoring on training data would
    report how well the model memorised, not how well it generalises.

    Args:
        model (Pipeline): Fitted pipeline from fit_model().
        X_test (pd.DataFrame): Test features (output of split()).
        y_test (pd.Series): True test labels.

    Returns:
        dict: {"accuracy", "roc_auc", "precision", "recall"}, each a float rounded to 3 places.
    """
    # prediction of either class 0 or 1 (non-diabetic or diabetic)
    y_pred = model.predict(X_test)
    # the probability of class 1 (diabetic)
    y_proba = model.predict_proba(X_test)[:, 1]
    # return the four metrics 
    return {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 3),
        "roc_auc": round(float(roc_auc_score(y_test, y_proba)), 3),
        "precision": round(float(precision_score(y_test, y_pred)), 3),
        "recall": round(float(recall_score(y_test, y_pred)), 3),
    }