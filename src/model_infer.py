from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from src.feature_engine import FEATURE_COLUMNS


class ModelInfer:
    def __init__(self, model_path: str = "models/model.joblib"):
        self.model = joblib.load(Path(model_path))

    def predict_signal(self, row: pd.Series, buy_th: float, sell_th: float):
        x = pd.DataFrame([row[FEATURE_COLUMNS].to_dict()], columns=FEATURE_COLUMNS)
        probs = self.model.predict_proba(x)[0]
        classes = list(self.model.classes_)

        p_buy = probs[classes.index(1)] if 1 in classes else 0.0
        p_sell = probs[classes.index(-1)] if -1 in classes else 0.0
        p_no = probs[classes.index(0)] if 0 in classes else 0.0

        if p_buy >= buy_th and p_buy > p_sell:
            return "BUY", float(p_buy), f"model_proba_buy={p_buy:.3f} p_no={p_no:.3f}"
        if p_sell >= sell_th and p_sell > p_buy:
            return "SELL", float(p_sell), f"model_proba_sell={p_sell:.3f} p_no={p_no:.3f}"
        return "NO_TRADE", float(np.max([p_no, p_buy, p_sell])), f"insufficient_edge p_buy={p_buy:.3f} p_sell={p_sell:.3f}"
