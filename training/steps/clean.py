import numpy as np
import pandas as pd

def clean(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """
    Clean the raw dataset according to the training configuration.

    Args:
        df (pd.DataFrame): The raw dataset as a pandas DataFrame.
        cfg (dict): The training configuration dictionary.

    Returns:
        pd.DataFrame: The cleaned dataset.
    """
    #create copy of df
    df = df.copy()

    #camel case to snake case
    df = df.rename(columns=cfg["rename"])

    #mark impossible values (datasets with impossible values will not be accepted)
    missing = cfg.get("clean", {}).get("treat_as_missing")
    if missing:
        cols = missing["columns"]
        df[cols] = df[cols].replace(missing["values"], np.nan)
    
    
    return df