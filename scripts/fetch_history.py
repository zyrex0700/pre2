from pathlib import Path

from src.config import ensure_runtime_dirs, load_config, load_mt5_credentials
from src.data_cleaner import DataCleaner
from src.data_collector import DataCollector
from src.monitoring import get_logger
from src.mt5_connector import MT5Connector


def main():
    rt = load_config()
    ensure_runtime_dirs(rt.cfg)
    logger = get_logger("fetch")
    conn = MT5Connector(load_mt5_credentials(), logger)
    if not conn.initialize():
        raise SystemExit(1)

    collector = DataCollector(conn, rt.cfg, logger)
    cleaner = DataCleaner()
    tf = rt.cfg["app"]["timeframe"]
    lookback = rt.cfg["app"]["lookback_bars"]

    for symbol in rt.symbols:
        df = collector.fetch_history(symbol, tf, lookback)
        clean = cleaner.clean(df)
        path = collector.save_raw(symbol, tf, clean)
        print(f"saved {symbol} -> {path} rows={len(clean)}")

    conn.shutdown()


if __name__ == "__main__":
    main()
