from __future__ import annotations

import pandas as pd


class DataCleaner:
    @staticmethod
    def clean(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        out = df.copy()
        out = out.drop_duplicates(subset=["time"]).sort_values("time")
        out = out.set_index("time")
        full_idx = pd.date_range(out.index.min(), out.index.max(), freq=out.index.inferred_freq or "15min", tz="UTC")
        out = out.reindex(full_idx)
        out[["open", "high", "low", "close"]] = out[["open", "high", "low", "close"]].ffill()
        out["tick_volume"] = out["tick_volume"].fillna(0)
        out = out.dropna(subset=["close"])
        out = out.reset_index(names="time")
        return out
