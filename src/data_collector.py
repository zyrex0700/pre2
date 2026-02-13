from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

from src.utils import ensure_dir


TIMEFRAME_MAP = {
    "M15": 15,
    "H1": 60,
}


class DataCollector:
    def __init__(self, connector, cfg: dict, logger):
        self.connector = connector
        self.cfg = cfg
        self.logger = logger

    def _tf_const(self, timeframe: str):
        mt5 = self.connector.mt5
        mapping = {"M15": mt5.TIMEFRAME_M15, "H1": mt5.TIMEFRAME_H1}
        return mapping[timeframe]

    def fetch_history(self, symbol: str, timeframe: str, lookback_bars: int) -> pd.DataFrame:
        minutes = TIMEFRAME_MAP[timeframe]
        end = datetime.now(timezone.utc)
        start = end - timedelta(minutes=minutes * lookback_bars)
        df = self.connector.fetch_rates(symbol, self._tf_const(timeframe), start, end)
        if not df.empty:
            df["symbol"] = symbol
            df["timeframe"] = timeframe
        return df

    def save_raw(self, symbol: str, timeframe: str, df: pd.DataFrame) -> Path:
        raw_dir = ensure_dir(self.cfg["data"]["raw_dir"])
        path = raw_dir / f"{symbol}_{timeframe}.parquet"
        df.to_parquet(path, index=False)
        self.logger.info(f"Saved raw data {path} rows={len(df)}")
        return path
