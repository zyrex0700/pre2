import pandas as pd

from src.feature_engine import FEATURE_COLUMNS, FeatureEngine


def test_feature_columns_created():
    n = 120
    t = pd.date_range("2025-01-01", periods=n, freq="15min", tz="UTC")
    df = pd.DataFrame(
        {
            "time": t,
            "open": [1 + i * 0.001 for i in range(n)],
            "high": [1.01 + i * 0.001 for i in range(n)],
            "low": [0.99 + i * 0.001 for i in range(n)],
            "close": [1 + i * 0.001 for i in range(n)],
            "tick_volume": [100] * n,
        }
    )
    fe = FeatureEngine()
    out = fe.transform(df)
    for c in FEATURE_COLUMNS:
        assert c in out.columns
    assert len(out) > 0
