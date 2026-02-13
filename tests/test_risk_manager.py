from src.risk_manager import RiskManager, RiskState


CFG = {
    "risk": {
        "risk_per_trade": 0.005,
        "max_daily_loss": 0.02,
        "max_weekly_loss": 0.05,
        "max_trades_per_day": 3,
        "max_consecutive_errors": 3,
        "spread_max_points": 35,
        "min_stop_points": 80,
        "kill_switch_enabled": True,
    }
}


def test_pre_trade_rejects_spread():
    rm = RiskManager(CFG)
    st = RiskState(10000, 10000)
    ok, reason = rm.check_pre_trade(40, st, 10000)
    assert not ok
    assert "spread" in reason


def test_position_size_positive():
    rm = RiskManager(CFG)
    lots = rm.position_size(balance=10000, stop_points=100, point=0.0001, tick_value=1.0)
    assert lots >= 0.01
