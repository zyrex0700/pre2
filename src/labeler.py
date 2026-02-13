from __future__ import annotations

import numpy as np
import pandas as pd


class TripleBarrierLabeler:
    def __init__(self, horizon_bars: int = 12, tp_mult: float = 1.5, sl_mult: float = 1.0):
        self.horizon_bars = horizon_bars
        self.tp_mult = tp_mult
        self.sl_mult = sl_mult

    def label(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        out["label"] = 0
        close = out["close"].values
        atr = out["atr_14"].values

        for i in range(len(out) - self.horizon_bars):
            entry = close[i]
            tp = entry + self.tp_mult * atr[i]
            sl = entry - self.sl_mult * atr[i]
            window = close[i + 1 : i + self.horizon_bars + 1]
            hit_tp = np.where(window >= tp)[0]
            hit_sl = np.where(window <= sl)[0]

            if len(hit_tp) == 0 and len(hit_sl) == 0:
                out.loc[i, "label"] = 0
            elif len(hit_tp) > 0 and (len(hit_sl) == 0 or hit_tp[0] < hit_sl[0]):
                out.loc[i, "label"] = 1
            else:
                out.loc[i, "label"] = -1

        return out.iloc[: len(out) - self.horizon_bars].reset_index(drop=True)
