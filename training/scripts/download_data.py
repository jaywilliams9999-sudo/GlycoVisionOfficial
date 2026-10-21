"""Download the raw datasets into data/raw/. Run from training/: python scripts/download_data.py"""
import urllib.request
from pathlib import Path

import pandas as pd

# scripts/download_data.py -> parents[0]=scripts, [1]=training, [2]=repo root
RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"

DATASETS = {
    "pima.csv": "https://raw.githubusercontent.com/npradaschnor/Pima-Indians-Diabetes-Dataset/master/diabetes.csv",
    "brfss.csv": "https://archive.ics.uci.edu/static/public/891/data.csv",
}
EXPECTED_ROWS = {"pima.csv": 768, "brfss.csv": 253_680}

# Zero counts of the untouched Pima file. A pre-imputed copy (which leaks the
# target into Insulin) has far fewer zeros, so this catches the wrong download.
PIMA_ZEROS = {"Glucose": 5, "BloodPressure": 35, "SkinThickness": 227, "Insulin": 374, "BMI": 11}


def verify(name: str, path: Path) -> None:
    """Raise ValueError if the file is not the known-good version of the dataset."""
    df = pd.read_csv(path)
    if len(df) != EXPECTED_ROWS[name]:
        raise ValueError(f"{name} has {len(df)} rows, expected {EXPECTED_ROWS[name]}.")
    if name == "pima.csv":
        zeros = {col: int((df[col] == 0).sum()) for col in PIMA_ZEROS}
        if zeros != PIMA_ZEROS:
            raise ValueError(f"pima.csv zero counts {zeros} != {PIMA_ZEROS}. Wrong or pre-imputed copy: delete it and rerun.")


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for name, url in DATASETS.items():
        path = RAW_DIR / name
        if path.exists():
            print(f"{name}: already present, verifying")
        else:
            print(f"{name}: downloading {url}")
            urllib.request.urlretrieve(url, path)
        verify(name, path)
        print(f"{name}: OK")


if __name__ == "__main__":
    main()