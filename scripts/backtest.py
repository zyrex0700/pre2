try:
    from scripts._bootstrap import bootstrap_project_root
except ModuleNotFoundError:
    from _bootstrap import bootstrap_project_root

bootstrap_project_root()

from pathlib import Path

import pandas as pd

from src.backtester import Backtester
from src.config import ensure_runtime_dirs, load_config
from src.model_infer import ModelInfer
from src.monitoring import get_logger


def main():
    rt = load_config()
    ensure_runtime_dirs(rt.cfg)
    logger = get_logger("backtest")

    label_path = Path(rt.cfg["data"]["label_dir"]) / "labeled.parquet"
    if not label_path.exists():
        raise FileNotFoundError("Run scripts/train_model.py first")
    df = pd.read_parquet(label_path)
    infer = ModelInfer("models/model.joblib")
    bt = Backtester(rt.cfg, infer, logger)
    result = bt.run(df)
    trades_path, metrics_path = bt.save(result)

    print("Backtest metrics:")
    print(result.metrics)
    print(f"saved trades: {trades_path}")
    print(f"saved metrics: {metrics_path}")


if __name__ == "__main__":
    main()
