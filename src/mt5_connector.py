from __future__ import annotations

import importlib
from datetime import datetime
from typing import Optional

import pandas as pd

from src.config import MT5Credentials


class MT5Connector:
    def __init__(self, credentials: MT5Credentials, logger):
        self.credentials = credentials
        self.logger = logger
        self.mt5 = None

    def _load_mt5(self):
        if self.mt5 is None:
            self.mt5 = importlib.import_module("MetaTrader5")
        return self.mt5

    def initialize(self) -> bool:
        try:
            mt5 = self._load_mt5()
        except ModuleNotFoundError:
            self.logger.error("MetaTrader5 package is not available")
            return False

        kwargs = {"login": self.credentials.login, "password": self.credentials.password, "server": self.credentials.server}
        if self.credentials.path:
            kwargs["path"] = self.credentials.path

        ok = mt5.initialize(**kwargs)
        if not ok:
            self.logger.error(f"MT5 initialize failed: {mt5.last_error()}")
            return False
        return True

    def shutdown(self) -> None:
        if self.mt5 is not None:
            self.mt5.shutdown()

    def health_check(self, symbols: list[str]) -> dict:
        out = {"connected": False, "account": None, "symbols": {}, "last_error": None}
        out["connected"] = self.initialize()
        if not out["connected"]:
            out["last_error"] = str(self.last_error())
            return out
        mt5 = self.mt5
        account = mt5.account_info()
        out["account"] = account._asdict() if account else None

        for s in symbols:
            sel = mt5.symbol_select(s, True)
            out["symbols"][s] = bool(sel)
        out["last_error"] = mt5.last_error()
        return out

    def fetch_rates(self, symbol: str, timeframe: int, start: datetime, end: datetime) -> pd.DataFrame:
        mt5 = self.mt5
        rates = mt5.copy_rates_range(symbol, timeframe, start, end)
        if rates is None:
            raise RuntimeError(f"copy_rates_range failed: {mt5.last_error()}")
        df = pd.DataFrame(rates)
        if df.empty:
            return df
        df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
        df = df.drop_duplicates(subset=["time"]).sort_values("time")
        return df

    def get_symbol_tick(self, symbol: str):
        return self.mt5.symbol_info_tick(symbol)

    def order_send(self, request: dict):
        return self.mt5.order_send(request)

    def positions_get(self, symbol: Optional[str] = None):
        return self.mt5.positions_get(symbol=symbol)

    def symbol_info(self, symbol: str):
        return self.mt5.symbol_info(symbol)

    def last_error(self):
        if self.mt5 is None:
            return (9999, "MetaTrader5 missing")
        return self.mt5.last_error()
