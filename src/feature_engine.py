from __future__ import annotations

import numpy as np
import pandas as pd


class FeatureEngine:
    @staticmethod
    def rsi(series: pd.Series, period: int = 14) -> pd.Series:
        delta = series.diff()
        gain = delta.clip(lower=0).rolling(period).mean()
        loss = -delta.clip(upper=0).rolling(period).mean()
        rs = gain / loss.replace(0, np.nan)
        return 100 - (100 / (1 + rs))

    @staticmethod
    def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        hl = df["high"] - df["low"]
        hc = (df["high"] - df["close"].shift()).abs()
        lc = (df["low"] - df["close"].shift()).abs()
        tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
        return tr.rolling(period).mean()

    @staticmethod
    def macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        ema_fast = close.ewm(span=fast, adjust=False).mean()
        ema_slow = close.ewm(span=slow, adjust=False).mean()
        line = ema_fast - ema_slow
        sig = line.ewm(span=signal, adjust=False).mean()
        hist = line - sig
        return line, sig, hist

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        out["returns"] = out["close"].pct_change()
        out["log_returns"] = np.log(out["close"] / out["close"].shift(1))
        out["roll_mean_10"] = out["close"].rolling(10).mean()
        out["roll_std_10"] = out["close"].rolling(10).std()
        out["atr_14"] = self.atr(out, 14)
        out["rsi_14"] = self.rsi(out["close"], 14)
        macd_line, macd_sig, macd_hist = self.macd(out["close"])
        out["macd"] = macd_line
        out["macd_signal"] = macd_sig
        out["macd_hist"] = macd_hist
        out["hour"] = out["time"].dt.hour
        out["dow"] = out["time"].dt.dayofweek
        out = out.dropna().reset_index(drop=True)
        return out


FEATURE_COLUMNS = [
    "returns",
    "log_returns",
    "roll_mean_10",
    "roll_std_10",
    "atr_14",
    "rsi_14",
    "macd",
    "macd_signal",
    "macd_hist",
    "hour",
    "dow",
]
