"""Choose the Low/Moderate and Moderate/High cut-offs from data instead of fixed numbers.

Both rules describe the model, not the population, so they keep their meaning in a
clinic whose patients are more or less likely to have diabetes than the training data:
  moderate: the highest line that still flags `low_recall` of diabetic patients,
            so a Low result rarely belongs to someone with diabetes.
  high:     the lowest line that keeps `high_specificity` of non-diabetic patients
            below it, so few people without diabetes are told High.
"""
import math

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_val_predict

from steps.train import build_pipeline


def thresholds_from_scores(y, scores, low_recall: float, high_specificity: float) -> dict:
    """
    Apply the two rules to known labels and scores.

    Rounded to 3 decimals in the safe direction (moderate down, high up), so rounding
    never breaks either target.

    Raises ValueError if moderate would not sit below high: the model can't separate
    the classes well enough for three bands.
    """
    y = np.asarray(y).astype(bool)
    s = np.asarray(scores, dtype=float)
    pos, neg = np.sort(s[y]), np.sort(s[~y])

    # at least ceil(low_recall * n) diabetic patients must score >= moderate
    must_flag = math.ceil(low_recall * len(pos))
    moderate = pos[len(pos) - must_flag]

    # at least ceil(high_specificity * n) others must score < high, i.e. high must be
    # strictly above the highest of those scores
    must_clear = math.ceil(high_specificity * len(neg))
    highest_cleared = neg[must_clear - 1]

    moderate = math.floor(round(moderate * 1000, 6)) / 1000
    high = (math.floor(round(highest_cleared * 1000, 6)) + 1) / 1000  # next 0.001 above it
    if not 0 < moderate < high < 1:
        # happens when the model separates the classes so well that one line meets both
        # targets, leaving no room for a Moderate band; pick stricter targets instead
        raise ValueError(f"No Moderate band: moderate={moderate} is not below high={high}.")
    return {"moderate": moderate, "high": high}


def choose_thresholds(X_train: pd.DataFrame, y_train: pd.Series, cfg: dict) -> dict:
    """
    Pick the cut-offs from cross-validated scores on the TRAINING split only.

    Each patient is scored by a model that never saw them (5-fold cross-validation),
    which mimics a new patient. The test split stays untouched so its metrics remain honest.
    """
    policy = cfg["risk_policy"]
    cv = StratifiedKFold(policy["cv_folds"], shuffle=True, random_state=cfg["split"]["random_state"])
    scores = cross_val_predict(build_pipeline(cfg), X_train, y_train, cv=cv, method="predict_proba")[:, 1]
    return thresholds_from_scores(y_train, scores, policy["low_recall"], policy["high_specificity"])
