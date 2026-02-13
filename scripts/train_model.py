try:
    from scripts._bootstrap import bootstrap_project_root
except ModuleNotFoundError:
    from _bootstrap import bootstrap_project_root

bootstrap_project_root()

from pathlib import Path

import pandas as pd

from src.config import ensure_runtime_dirs, load_config
from src.feature_engine import FeatureEngine
from src.labeler import TripleBarrierLabeler
from src.model_train import ModelTrainer
from src.monitoring import get_logger


def main():
    rt = load_config()
    ensure_runtime_dirs(rt.cfg)
    logger = get_logger("train")
    tf = rt.cfg["app"]["timeframe"]

    frames = []
    for symbol in rt.symbols:
        p = Path(rt.cfg["data"]["raw_dir"]) / f"{symbol}_{tf}.parquet"
        if not p.exists():
            raise FileNotFoundError(f"Missing raw data for {symbol}: {p}")
        df = pd.read_parquet(p)
        df["symbol"] = symbol
        frames.append(df)

    all_df = pd.concat(frames).sort_values("time").reset_index(drop=True)
    fe = FeatureEngine()
    feat = fe.transform(all_df)

    lbl = TripleBarrierLabeler(horizon_bars=rt.cfg["app"]["horizon_bars"])
    labeled = lbl.label(feat)

    feat_path = Path(rt.cfg["data"]["feature_dir"]) / "features.parquet"
    label_path = Path(rt.cfg["data"]["label_dir"]) / "labeled.parquet"
    feat.to_parquet(feat_path, index=False)
    labeled.to_parquet(label_path, index=False)

    trainer = ModelTrainer(random_state=rt.cfg["model"]["random_state"])
    metrics = trainer.train(labeled)
    model_path = trainer.save("models/model.joblib")

    logger.info(f"train_metrics={metrics}")
    print(metrics["classification_report"])
    print(f"model saved: {model_path}")


if __name__ == "__main__":
    main()
