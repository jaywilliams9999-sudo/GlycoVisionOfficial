"""Score a fitted pipeline on held-out test data."""
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score
from sklearn.pipeline import Pipeline


def score(model: Pipeline, X_test: pd.DataFrame, y_test: pd.Series, thresholds: dict) -> dict:
    """
    Compute test-set metrics for metadata.json.

    Only ever pass the TEST split here. Scoring on training data would
    report how well the model memorised, not how well it generalises.

    Args:
        model (Pipeline): Fitted pipeline from fit_model().
        X_test (pd.DataFrame): Test features (output of split()).
        y_test (pd.Series): True test labels.
        thresholds (dict): {"moderate", "high"} cut-offs from choose_thresholds().

    Returns:
        dict: accuracy, roc_auc, precision and recall (at the default 0.5), plus how the
        risk bands did on unseen patients, each a float rounded to 3 places.
    """
    # prediction of either class 0 or 1 (non-diabetic or diabetic)
    y_pred = model.predict(X_test)
    # the probability of class 1 (diabetic)
    y_proba = model.predict_proba(X_test)[:, 1]
    y = y_test.to_numpy().astype(bool)
    high = y_proba >= thresholds["high"]

    def r(x) -> float:
        return round(float(x), 3)

    return {
        "accuracy": r(accuracy_score(y_test, y_pred)),
        "roc_auc": r(roc_auc_score(y_test, y_proba)),
        "precision": r(precision_score(y_test, y_pred)),
        "recall": r(recall_score(y_test, y_pred)),
        # diabetic patients scored at or above the Low line (target: risk_policy.low_recall)
        "low_line_recall": r((y_proba[y] >= thresholds["moderate"]).mean()),
        # non-diabetic patients kept below the High line (target: risk_policy.high_specificity)
        "high_line_specificity": r((~high[~y]).mean()),
        # share of High results that really had diabetes (depends on how common diabetes is)
        "high_precision": r(y[high].mean()) if high.any() else 0.0,
        "share_low": r((y_proba < thresholds["moderate"]).mean()),
        "share_high": r(high.mean()),
    }
