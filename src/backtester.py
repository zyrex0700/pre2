from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from src.feature_engine import FEATURE_COLUMNS


@dataclass
class BacktestResult:
    trades: pd.DataFrame
    metrics: dict


class Backtester:
    def __init__(self, cfg: dict, infer_model, logger):
        self.cfg = cfg
        self.model = infer_model
        self.logger = logger

    def run(self, df: pd.DataFrame) -> BacktestResult:
        balance = self.cfg["backtest"]["initial_balance"]
        spread = self.cfg["backtest"]["spread_points"]
        slippage = self.cfg["backtest"]["slippage_points"]
        commission = self.cfg["backtest"]["commission_per_lot"]
        rr = self.cfg["backtest"]["risk_reward"]

        rows = []
        for i in range(len(df) - 1):
            row = df.iloc[i]
            x = row[FEATURE_COLUMNS].values.reshape(1, -1)
            probs = self.model.model.predict_proba(x)[0]
            classes = list(self.model.model.classes_)
            p_buy = probs[classes.index(1)] if 1 in classes else 0
            p_sell = probs[classes.index(-1)] if -1 in classes else 0
            if p_buy < self.cfg["model"]["confidence_buy"] and p_sell < self.cfg["model"]["confidence_sell"]:
                continue
            side = 1 if p_buy > p_sell else -1
            entry = row["close"] + side * (spread + slippage) * 0.00001
            next_close = df.iloc[i + 1]["close"]
            pnl_points = (next_close - entry) * side
            pnl = pnl_points * 100000 - commission
            balance += pnl
            rows.append({"time": row["time"], "symbol": row.get("symbol", "UNK"), "side": side, "pnl": pnl, "balance": balance})

        trades = pd.DataFrame(rows)
        if trades.empty:
            metrics = {"trades": 0, "pnl": 0.0, "winrate": 0.0, "profit_factor": 0.0, "max_drawdown": 0.0}
        else:
            wins = trades[trades["pnl"] > 0]
            losses = trades[trades["pnl"] <= 0]
            eq = trades["balance"]
            rolling_max = eq.cummax()
            dd = ((rolling_max - eq) / rolling_max).max()
            metrics = {
                "trades": int(len(trades)),
                "pnl": float(trades["pnl"].sum()),
                "winrate": float((trades["pnl"] > 0).mean()),
                "profit_factor": float(wins["pnl"].sum() / abs(losses["pnl"].sum())) if len(losses) else float("inf"),
                "max_drawdown": float(dd),
                "risk_reward": rr,
            }
        return BacktestResult(trades=trades, metrics=metrics)

    @staticmethod
    def save(result: BacktestResult, out_dir: str = "reports") -> tuple[Path, Path]:
        p = Path(out_dir)
        p.mkdir(parents=True, exist_ok=True)
        trades_path = p / "backtest_trades.csv"
        metrics_path = p / "backtest_metrics.csv"
        result.trades.to_csv(trades_path, index=False)
        pd.DataFrame([result.metrics]).to_csv(metrics_path, index=False)
        return trades_path, metrics_path
