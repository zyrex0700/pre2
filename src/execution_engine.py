from __future__ import annotations

import time


class ExecutionEngine:
    def __init__(self, connector, risk_manager, cfg: dict, logger):
        self.connector = connector
        self.risk_manager = risk_manager
        self.cfg = cfg
        self.logger = logger

    def place_market_order(self, symbol: str, action: str, lot: float, sl: float, tp: float, comment: str = "ai-bot"):
        mt5 = self.connector.mt5
        tick = self.connector.get_symbol_tick(symbol)
        if tick is None:
            return None, "no tick"

        order_type = mt5.ORDER_TYPE_BUY if action == "BUY" else mt5.ORDER_TYPE_SELL
        price = tick.ask if action == "BUY" else tick.bid

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": order_type,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": self.cfg["execution"]["deviation"],
            "magic": self.cfg["execution"]["magic_number"],
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        attempts = self.cfg["execution"]["retry_attempts"]
        backoff = self.cfg["execution"]["retry_backoff_sec"]
        for i in range(attempts):
            result = self.connector.order_send(request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                return result, "filled"
            self.logger.error(f"order_send failed attempt={i+1}/{attempts} result={result}")
            time.sleep(backoff * (i + 1))
        return result, "failed"
