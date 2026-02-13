try:
    from scripts._bootstrap import bootstrap_project_root
except ModuleNotFoundError:
    from _bootstrap import bootstrap_project_root

bootstrap_project_root()

from src.config import load_config, load_mt5_credentials
from src.monitoring import get_logger
from src.mt5_connector import MT5Connector


def main():
    rt = load_config()
    logger = get_logger("health")
    conn = MT5Connector(load_mt5_credentials(), logger)
    result = conn.health_check(rt.symbols)
    logger.info(f"health_check={result}")
    print(result)
    conn.shutdown()


if __name__ == "__main__":
    main()
