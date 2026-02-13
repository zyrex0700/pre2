from __future__ import annotations


class PositionManager:
    def __init__(self, connector, logger):
        self.connector = connector
        self.logger = logger

    def has_open_position(self, symbol: str) -> bool:
        positions = self.connector.positions_get(symbol=symbol)
        return positions is not None and len(positions) > 0
