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

    def _symbol_spec(self, symbol: str) -> dict:
        specs = self.cfg["backtest"].get("symbol_specs", {})
        # Conservative fallback to avoid exaggerated pnl if symbol spec is missing.
        return specs.get(
            symbol,
            {
                "point": 0.0001,
                "point_value_per_lot": 1.0,
                "lot": self.cfg["backtest"].get("default_lot", 0.1),
            },
        )

    def _price_with_cost(self, price: float, side: int, point: float, spread_points: float, slippage_points: float) -> float:
        # side=1 (BUY): worse entry/exit on ask; side=-1 (SELL): worse on bid
        return price + side * (spread_points + slippage_points) * point

    def run(self, df: pd.DataFrame) -> BacktestResult:
        balance = float(self.cfg["backtest"]["initial_balance"])
        spread_points = float(self.cfg["backtest"]["spread_points"])
        slippage_points = float(self.cfg["backtest"]["slippage_points"])
        commission_per_lot = float(self.cfg["backtest"]["commission_per_lot"])
        rr = self.cfg["backtest"]["risk_reward"]

        rows = []
        for i in range(len(df) - 1):
            row = df.iloc[i]
            symbol = row.get("symbol", "UNK")
            spec = self._symbol_spec(symbol)
            point = float(spec["point"])
            point_value_per_lot = float(spec["point_value_per_lot"])
            lot = float(spec["lot"])

            x = row[FEATURE_COLUMNS].values.reshape(1, -1)
            probs = self.model.model.predict_proba(x)[0]
            classes = list(self.model.model.classes_)
            p_buy = probs[classes.index(1)] if 1 in classes else 0
            p_sell = probs[classes.index(-1)] if -1 in classes else 0
            if p_buy < self.cfg["model"]["confidence_buy"] and p_sell < self.cfg["model"]["confidence_sell"]:
                continue

            side = 1 if p_buy > p_sell else -1
            raw_entry = float(row["close"])
            raw_exit = float(df.iloc[i + 1]["close"])

            entry = self._price_with_cost(raw_entry, side, point, spread_points, slippage_points)
            exit_price = self._price_with_cost(raw_exit, -side, point, spread_points, slippage_points)

            move_points = ((exit_price - entry) / point) * side
            gross_pnl = move_points * point_value_per_lot * lot
            net_pnl = gross_pnl - (commission_per_lot * lot)

            balance += net_pnl
            rows.append(
                {
                    "time": row["time"],
                    "symbol": symbol,
                    "side": side,
                    "lot": lot,
                    "move_points": move_points,
                    "pnl": net_pnl,
                    "balance": balance,
                }
            )

        trades = pd.DataFrame(rows)
        if trades.empty:
            metrics = {"trades": 0, "pnl": 0.0, "winrate": 0.0, "profit_factor": 0.0, "max_drawdown": 0.0}
        else:
            wins = trades[trades["pnl"] > 0]
            losses = trades[trades["pnl"] <= 0]
            eq = trades["balance"]
            rolling_max = eq.cummax()
            dd = ((rolling_max - eq) / rolling_max.replace(0, 1e-9)).max()
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
