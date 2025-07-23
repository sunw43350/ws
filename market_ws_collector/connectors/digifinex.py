import json
import time
import zlib
import websockets

from config import DEFAULT_SYMBOLS, WS_ENDPOINTS
from models.base import MarketSnapshot, SubscriptionRequest
from connectors.base import BaseAsyncConnector

class Connector(BaseAsyncConnector):
    def __init__(self, exchange="digifinex", symbols=None, ws_url=None, queue=None):
        super().__init__(
            exchange=exchange,
            compression="zlib",
            ping_interval=30,
            ping_payload={"id": 999, "event": "server.ping"},
            pong_keywords=["pong"]
        )
        # super().__init__(exchange, compression="zlib")
        self.queue = queue
        self.ws_url = ws_url or WS_ENDPOINTS.get(exchange)

        self.raw_symbols = symbols or DEFAULT_SYMBOLS.get(exchange, [])
        self.formatted_symbols = [self.format_symbol(sym) for sym in self.raw_symbols]

        self.subscriptions = [
            SubscriptionRequest(symbol=sym, channel="ticker")
            for sym in self.formatted_symbols
        ]

        self.symbol_map = {
            sym: raw for sym, raw in zip(self.formatted_symbols, self.raw_symbols)
        }

    def format_symbol(self, generic_symbol: str) -> str:
        return generic_symbol.upper().replace("-", "").replace("_", "") + "PERP"

    def build_sub_msg(self) -> dict:
        return {
            "event": "ticker.subscribe",
            "id": 1,
            "instrument_ids": self.formatted_symbols
        }

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url)
        self.log(f"✅ Digifinex WebSocket 已连接 → {self.ws_url}")

    async def subscribe(self):
        msg = self.build_sub_msg()
        await self.ws.send(json.dumps(msg))
        await self.ws.send(json.dumps({"id": 99, "event": "server.ping"}))
        self.log(f"📨 已发送订阅请求: {msg}")

    async def handle_message(self, data):
        if data.get("event") == "ticker.update" and "data" in data:
            tick = data["data"]
            symbol = tick.get("instrument_id")
            raw_symbol = self.symbol_map.get(symbol, symbol)

            bid1 = float(tick.get("best_bid", 0.0))
            ask1 = float(tick.get("best_ask", 0.0))
            bid_vol1 = float(tick.get("best_bid_size", 0.0))
            ask_vol1 = float(tick.get("best_ask_size", 0.0))
            total_volume = float(tick.get("volume_token_24h", tick.get("volume_24h", 0.0)))
            timestamp = int(tick.get("timestamp", time.time() * 1000))

            snapshot = MarketSnapshot(
                exchange=self.exchange_name,
                symbol=symbol,
                raw_symbol=raw_symbol,
                bid1=bid1,
                ask1=ask1,
                bid_vol1=bid_vol1,
                ask_vol1=ask_vol1,
                total_volume=total_volume,
                timestamp=timestamp
            )

            if self.queue:
                await self.queue.put(snapshot)
