from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RiskState:
    starting_balance_day: float
    starting_balance_week: float
    trades_today: int = 0
    consecutive_errors: int = 0


class RiskManager:
    def __init__(self, cfg: dict):
        risk_cfg = cfg["risk"]
        self.risk_per_trade = risk_cfg["risk_per_trade"]
        self.max_daily_loss = risk_cfg["max_daily_loss"]
        self.max_weekly_loss = risk_cfg["max_weekly_loss"]
        self.max_trades_per_day = risk_cfg["max_trades_per_day"]
        self.max_consecutive_errors = risk_cfg["max_consecutive_errors"]
        self.spread_max_points = risk_cfg["spread_max_points"]
        self.min_stop_points = risk_cfg["min_stop_points"]
        self.kill_switch_enabled = risk_cfg.get("kill_switch_enabled", True)

    def check_pre_trade(self, spread_points: float, state: RiskState, balance: float) -> tuple[bool, str]:
        if spread_points > self.spread_max_points:
            return False, f"spread too high: {spread_points} > {self.spread_max_points}"
        if state.trades_today >= self.max_trades_per_day:
            return False, "max_trades_per_day reached"
        if self.kill_switch_enabled:
            daily_dd = (state.starting_balance_day - balance) / max(state.starting_balance_day, 1e-9)
            weekly_dd = (state.starting_balance_week - balance) / max(state.starting_balance_week, 1e-9)
            if daily_dd >= self.max_daily_loss:
                return False, "kill_switch daily loss reached"
            if weekly_dd >= self.max_weekly_loss:
                return False, "kill_switch weekly loss reached"
            if state.consecutive_errors >= self.max_consecutive_errors:
                return False, "kill_switch consecutive errors reached"
        return True, "ok"

    def position_size(self, balance: float, stop_points: float, point: float, tick_value: float) -> float:
        stop_points = max(stop_points, self.min_stop_points)
        risk_amount = balance * self.risk_per_trade
        value_per_point = tick_value / point if point > 0 else 1.0
        lots = risk_amount / max(stop_points * value_per_point, 1e-9)
        return max(round(lots, 2), 0.01)
