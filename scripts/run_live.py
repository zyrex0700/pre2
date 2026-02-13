import time
from datetime import datetime

from src.config import ensure_runtime_dirs, load_config, load_mt5_credentials
from src.data_collector import DataCollector
from src.feature_engine import FeatureEngine
from src.monitoring import get_logger, send_telegram
from src.mt5_connector import MT5Connector
from src.position_manager import PositionManager
from src.risk_manager import RiskManager, RiskState
from src.signal_engine import SignalEngine
from src.execution_engine import ExecutionEngine


def main():
    rt = load_config()
    ensure_runtime_dirs(rt.cfg)
    logger = get_logger("live")
    logger.info(f"starting mode={rt.mode} auto_trade={rt.auto_trade}")

    if rt.mode == "live" and not rt.auto_trade:
        logger.warning("Live mode selected but AUTO_TRADE=false, running signal-only.")

    conn = MT5Connector(load_mt5_credentials(), logger)
    if not conn.initialize():
        raise SystemExit(1)

    sig_engine = SignalEngine(rt.cfg)
    risk = RiskManager(rt.cfg)
    exec_engine = ExecutionEngine(conn, risk, rt.cfg, logger)
    pos_mgr = PositionManager(conn, logger)
    collector = DataCollector(conn, rt.cfg, logger)
    fe = FeatureEngine()

    account = conn.mt5.account_info()
    state = RiskState(starting_balance_day=account.balance, starting_balance_week=account.balance)

    while True:
        for symbol in rt.symbols:
            try:
                tf = rt.cfg["app"]["timeframe"]
                lookback = max(rt.cfg["app"]["lookback_bars"], 200)
                df = collector.fetch_history(symbol, tf, lookback)
                if df.empty:
                    continue
                feat = fe.transform(df)
                row = feat.iloc[-1]

                tick = conn.get_symbol_tick(symbol)
                if tick is None:
                    continue
                spread_points = (tick.ask - tick.bid) / conn.symbol_info(symbol).point

                ok, reason = risk.check_pre_trade(spread_points, state, account.balance)
                if not ok:
                    logger.warning(f"{symbol} NO_TRADE risk_filter: {reason}")
                    continue

                signal = sig_engine.generate(row, spread_points)
                logger.info(f"signal {symbol}: {signal}")
                if signal.action == "NO_TRADE" or pos_mgr.has_open_position(symbol):
                    continue

                if not rt.auto_trade:
                    logger.info(f"paper signal only {symbol}: {signal.action} conf={signal.confidence:.3f}")
                    continue

                info = conn.symbol_info(symbol)
                stop_points = abs(row["close"] - signal.sl) / info.point
                lot = risk.position_size(account.balance, stop_points, info.point, info.trade_tick_value)
                result, status = exec_engine.place_market_order(symbol, signal.action, lot, signal.sl, signal.tp)
                if status == "filled":
                    state.trades_today += 1
                    logger.info(f"order filled {symbol} lot={lot} result={result}")
                    send_telegram(f"Order filled {symbol} {signal.action} lot={lot}", rt.cfg["telegram"]["enabled"])
                else:
                    state.consecutive_errors += 1
                    logger.error(f"order failed {symbol} status={status} result={result}")
                    send_telegram(f"Order FAILED {symbol} status={status}", rt.cfg["telegram"]["enabled"])

            except Exception as exc:
                state.consecutive_errors += 1
                logger.exception(f"loop error for {symbol}: {exc}")
                send_telegram(f"Bot error {symbol}: {exc}", rt.cfg["telegram"]["enabled"])

        if state.consecutive_errors >= rt.cfg["risk"]["max_consecutive_errors"]:
            logger.error("Kill-switch triggered: consecutive errors")
            send_telegram("Kill-switch triggered: consecutive errors", rt.cfg["telegram"]["enabled"])
            break

        time.sleep(rt.cfg["app"]["poll_seconds"])

    conn.shutdown()


if __name__ == "__main__":
    main()
