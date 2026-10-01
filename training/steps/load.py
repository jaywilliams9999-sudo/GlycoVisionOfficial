"""Load raw dataset files named by training config."""
from pathlib import Path
import pandas as pd

def load_raw(cfg: dict) -> pd.DataFrame:
    """
    Read the csv and return it unmodified

    Args:
        cfg (dict): The training configuration dictionary.
    
    Will give a filenotfound error if needed csv is not downloaded.
    """
    path = Path(cfg["source"])
    if not path.exists():
        raise FileNotFoundError(f"File {path} does not exist. Please download the dataset first.")
    return pd.read_csv(path)