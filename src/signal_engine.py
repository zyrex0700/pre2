from __future__ import annotations

from src.model_infer import ModelInfer
from src.utils import Signal


class SignalEngine:
    def __init__(self, cfg: dict, model_path: str = "models/model.joblib"):
        self.cfg = cfg
        self.model = ModelInfer(model_path)

    def generate(self, row, side_spread_points: float) -> Signal:
        mcfg = self.cfg["model"]
        action, conf, reason = self.model.predict_signal(
            row, buy_th=mcfg["confidence_buy"], sell_th=mcfg["confidence_sell"]
        )
        atr = float(row["atr_14"])
        close = float(row["close"])
        if action == "BUY":
            sl = close - atr
            tp = close + atr * self.cfg["backtest"]["risk_reward"]
        elif action == "SELL":
            sl = close + atr
            tp = close - atr * self.cfg["backtest"]["risk_reward"]
        else:
            sl = 0.0
            tp = 0.0
        reason = f"{reason}; spread={side_spread_points:.1f}"
        return Signal(action=action, confidence=conf, entry_type="MARKET", sl=sl, tp=tp, reason=reason)
