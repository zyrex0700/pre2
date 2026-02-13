import numpy as np
import pandas as pd

from src.backtester import Backtester
from src.feature_engine import FEATURE_COLUMNS


class DummyModel:
    classes_ = np.array([-1, 0, 1])

    def predict_proba(self, x):
        # always prefer BUY
        return np.array([[0.1, 0.1, 0.8]])


class DummyInfer:
    def __init__(self):
        self.model = DummyModel()


def test_backtester_pnl_is_scaled_reasonably():
    n = 20
    t = pd.date_range("2025-01-01", periods=n, freq="15min", tz="UTC")
    base = np.linspace(1.1000, 1.1020, n)
    df = pd.DataFrame({"time": t, "close": base, "symbol": ["EURUSD"] * n})
    for c in FEATURE_COLUMNS:
        df[c] = 0.01

    cfg = {
        "model": {"confidence_buy": 0.5, "confidence_sell": 0.5},
        "backtest": {
            "initial_balance": 10000,
            "spread_points": 2,
            "slippage_points": 1,
            "commission_per_lot": 7.0,
            "risk_reward": 1.5,
            "default_lot": 0.1,
            "symbol_specs": {
                "EURUSD": {"point": 0.0001, "point_value_per_lot": 10.0, "lot": 0.1}
            },
        },
    }

    bt = Backtester(cfg, DummyInfer(), logger=None)
    result = bt.run(df)
    assert result.metrics["trades"] > 0
    # sanity guard: should not explode to absurd values
    assert abs(result.metrics["pnl"]) < 10_000
