"""Split cleaned data into training and testing"""
import pandas as pd
from sklearn.model_selection import train_test_split


def split(df: pd.DataFrame, cfg: dict) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Separate features from target and make a train/test split.

    Must run BEFORE any statistic is computed (e.g. imputation medians),
    so the test set never influences training.

    Args:
        df (pd.DataFrame): The cleaned dataset (output of clean()).
        cfg (dict): The training configuration dictionary.

    Returns:
        X_train, X_test, y_train, y_test
    """
    # only feature columns
    X = df[cfg["features"]]
    # the target column
    y = df[cfg["target"]]

    # read split settings
    test_size = cfg["split"]["test_size"]
    random_state = cfg["split"]["random_state"]
    stratify = y if cfg["split"]["stratify"] else None

    # return
    return train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=stratify)