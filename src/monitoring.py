from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import requests


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "time": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra"):
            payload["extra"] = record.extra
        return json.dumps(payload, ensure_ascii=False)


def get_logger(name: str = "bot", log_file: str = "logs/bot.log") -> logging.Logger:
    Path("logs").mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return logger

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(JsonFormatter())
    logger.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    logger.addHandler(sh)
    return logger


def send_telegram(message: str, enabled: bool = False) -> bool:
    if not enabled:
        return False
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    response = requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=10)
    return response.ok


def audit_log(logger: logging.Logger, event: str, payload: Dict[str, Any]) -> None:
    logger.info(event, extra={"extra": payload})
