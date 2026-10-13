"""Load raw dataset files named by training config."""
from pathlib import Path
import pandas as pd

# steps/load.py -> parents[0]=steps, [1]=training, [2]=repo root
REPO_ROOT = Path(__file__).resolve().parents[2]

def load_raw(cfg: dict) -> pd.DataFrame:
    """
    Read the csv and return it unmodified

    Args:
        cfg (dict): The training configuration dictionary.
    
    Will give a filenotfound error if needed csv is not downloaded.
    """
    path = REPO_ROOT / cfg["source"]
    if not path.exists():
        raise FileNotFoundError(f"File {path} does not exist. Please download the dataset first.")
    return pd.read_csv(path)