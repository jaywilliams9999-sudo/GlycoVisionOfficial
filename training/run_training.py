"""Train one model Run from training/: python run_training.py configs/clinical.yaml MAKE SURE YOU RUN WITH CONFIGS OR IT WILL NOT WORK"""
import argparse
import json
from pathlib import Path

import yaml

from steps.load import load_raw
from steps.clean import clean
from steps.split import split
from steps.train import fit_model
from steps.evaluate import score
from steps.save import write_model_store


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a GlycoVision model from a config file.")
    parser.add_argument("config", type=Path, help="Path to a YAML config, e.g. configs/clinical.yaml")
    args = parser.parse_args()

    cfg = yaml.safe_load(args.config.read_text())

    df = clean(load_raw(cfg), cfg)
    X_train, X_test, y_train, y_test = split(df, cfg)
    model = fit_model(X_train, y_train, cfg)
    metrics = score(model, X_test, y_test)
    out_dir = write_model_store(model, metrics, cfg)

    print(f"{cfg['model_version']} test metrics: {json.dumps(metrics)}")
    print(f"Saved to {out_dir}")


if __name__ == "__main__":
    main()