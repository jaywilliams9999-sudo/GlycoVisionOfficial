"""Turn raw SHAP output into the {feature, value, contribution} list the frontend charts."""
import pandas as pd

from app.ml.registry import ModelEntry

INDICATOR_PREFIX = "missingindicator_"


def explain(entry: ModelEntry, X: pd.DataFrame) -> list[dict]:
    """
    Per-feature contributions to the diabetic-class probability for one row.

    The imputer adds "missingindicator_<feature>" columns; their contribution is
    folded back into <feature>, so a clinician sees one bar per input they entered.
    Sorted by absolute contribution, largest first.
    """
    imputer = entry.model.named_steps["imputer"]
    X_imputed = imputer.transform(X)
    columns = imputer.get_feature_names_out()

    # shape (rows, columns, classes); take row 0, class 1 (diabetic)
    shap_row = entry.explainer.shap_values(X_imputed)[0, :, 1]

    contributions = {feature: 0.0 for feature in X.columns}
    for column, value in zip(columns, shap_row):
        contributions[column.removeprefix(INDICATOR_PREFIX)] += float(value)

    row = X.iloc[0]
    result = [
        {
            "feature": feature,
            "value": None if pd.isna(row[feature]) else float(row[feature]),
            "contribution": round(contribution, 4),
        }
        for feature, contribution in contributions.items()
    ]
    return sorted(result, key=lambda item: abs(item["contribution"]), reverse=True)