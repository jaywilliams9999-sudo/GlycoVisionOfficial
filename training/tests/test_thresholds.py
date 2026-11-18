"""Cut-off rules: Low line keeps recall >= target, High line keeps specificity >= target."""
import numpy as np
import pytest

from steps.thresholds import thresholds_from_scores

# 10 diabetic and 10 non-diabetic patients with hand-picked scores
POS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
NEG = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]


def labelled(pos, neg):
    return [1] * len(pos) + [0] * len(neg), pos + neg


def test_known_answer():
    y, s = labelled(POS, NEG)
    t = thresholds_from_scores(y, s, low_recall=0.9, high_specificity=0.9)
    # 9 of 10 diabetic scores are >= 0.2, so 0.2 is the highest line that still catches 90%
    assert t["moderate"] == 0.2
    # 9 of 10 non-diabetic scores (up to 0.8) must fall below the line: the first value above 0.8
    assert t["high"] == 0.801


def test_targets_hold_on_overlapping_scores():
    rng = np.random.default_rng(0)
    pos = list(rng.beta(4, 2, 500))   # diabetic patients tend to score high
    neg = list(rng.beta(2, 4, 2000))  # others tend to score low
    y, s = labelled(pos, neg)
    t = thresholds_from_scores(y, s, low_recall=0.9, high_specificity=0.9)

    assert np.mean(np.array(pos) >= t["moderate"]) >= 0.9
    assert np.mean(np.array(neg) < t["high"]) >= 0.9
    assert 0 < t["moderate"] < t["high"] < 1


def test_no_moderate_band_is_reported_instead_of_returning_crossed_lines():
    # near-perfect separation: one line meets both targets, so Low/High would overlap
    y, s = labelled([0.8, 0.85, 0.9, 0.95, 1.0], [0.0, 0.05, 0.1, 0.15, 0.2])
    with pytest.raises(ValueError, match="No Moderate band"):
        thresholds_from_scores(y, s, low_recall=0.9, high_specificity=0.9)


def test_rounding_never_breaks_a_target():
    # scores just past a 0.001 step must not be rounded onto the wrong side of the line
    y, s = labelled([0.2004, 0.5, 0.9], [0.1, 0.3, 0.7996])
    t = thresholds_from_scores(y, s, low_recall=1.0, high_specificity=1.0)
    assert t["moderate"] <= 0.2004 and t["high"] > 0.7996
