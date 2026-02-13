from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv

from src.utils import load_yaml


@dataclass
class MT5Credentials:
    login: int
    password: str
    server: str
    path: str | None


@dataclass
class RuntimeConfig:
    cfg: Dict[str, Any]
    mode: str
    auto_trade: bool
    symbols: List[str]



def load_config(config_path: str = "config.yaml") -> RuntimeConfig:
    load_dotenv()
    cfg = load_yaml(config_path)
    mode = os.getenv("BOT_MODE", cfg["app"]["mode"]).lower()
    auto_trade = os.getenv("AUTO_TRADE", "false").lower() == "true"
    symbols = cfg["app"].get("symbols", ["XAUUSD", "EURUSD"])

    for key in ["data", "model", "risk", "execution", "backtest", "app"]:
        if key not in cfg:
            raise ValueError(f"Missing config section: {key}")

    return RuntimeConfig(cfg=cfg, mode=mode, auto_trade=auto_trade, symbols=symbols)


def load_mt5_credentials() -> MT5Credentials:
    login = int(os.getenv("MT5_LOGIN", "0"))
    password = os.getenv("MT5_PASSWORD", "")
    server = os.getenv("MT5_SERVER", "")
    path = os.getenv("MT5_PATH", None)
    if login <= 0 or not password or not server:
        raise ValueError("MT5 credentials are missing. Set MT5_LOGIN, MT5_PASSWORD, MT5_SERVER in .env")
    return MT5Credentials(login=login, password=password, server=server, path=path)


def ensure_runtime_dirs(cfg: Dict[str, Any]) -> None:
    for key in ["raw_dir", "clean_dir", "feature_dir", "label_dir"]:
        Path(cfg["data"][key]).mkdir(parents=True, exist_ok=True)
    for folder in ["logs", "models", "reports"]:
        Path(folder).mkdir(parents=True, exist_ok=True)
