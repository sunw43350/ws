import asyncio
import json
import time
import websockets

from config import DEFAULT_SYMBOLS, WS_ENDPOINTS
from models.base import SubscriptionRequest, MarketSnapshot
from connectors.base import BaseAsyncConnector

class Connector(BaseAsyncConnector):
    def __init__(self, exchange="blofin", symbols=None, ws_url=None, queue=None):
        super().__init__(
            exchange=exchange,
            ping_interval=10,   # 或 None，表示不主动发 ping
            ping_payload="ping",
            pong_keywords=["pong"]
        )
        self.queue = queue
        self.ws_url = ws_url or WS_ENDPOINTS.get(exchange)

        self.raw_symbols = symbols or DEFAULT_SYMBOLS.get(exchange, [])
        self.formatted_symbols = [self.format_symbol(sym) for sym in self.raw_symbols]

        self.subscriptions = [
            SubscriptionRequest(symbol=sym, channel="tickers")
            for sym in self.formatted_symbols
        ]

        self.symbol_map = {
            sym: raw for sym, raw in zip(self.formatted_symbols, self.raw_symbols)
        }

    def format_symbol(self, generic_symbol: str) -> str:
        return generic_symbol.upper()

    def build_sub_msg(self, symbol: str) -> dict:
        return {
            "op": "subscribe",
            "args": [
                {
                    "channel": "tickers",
                    "instType": "CONTRACT",
                    "instId": symbol
                }
            ]
        }

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url)
        self.log(f"✅ BloFin WebSocket 已连接 → {self.ws_url}")

    async def subscribe(self):
        for req in self.subscriptions:
            msg = self.build_sub_msg(req.symbol)
            await self.ws.send(json.dumps(msg))
            self.log(f"📨 已订阅: tickers → {req.symbol}")
            await asyncio.sleep(0.1)

    async def handle_message(self, data):
        if "arg" in data and "data" in data:
            arg = data["arg"]
            symbol = arg.get("instId", "unknown")
            raw_symbol = self.symbol_map.get(symbol, symbol)

            item = data["data"][0]
            bid1 = float(item.get("bidPrice", 0.0))
            ask1 = float(item.get("askPrice", 0.0))
            bid_vol1 = float(item.get("bidSize", 0.0))
            ask_vol1 = float(item.get("askSize", 0.0))
            ts = int(item.get("ts", time.time() * 1000))
            total_volume = float(item.get("vol24h", 0.0))

            snapshot = MarketSnapshot(
                exchange=self.exchange_name,
                symbol=symbol,
                raw_symbol=raw_symbol,
                bid1=bid1,
                ask1=ask1,
                bid_vol1=bid_vol1,
                ask_vol1=ask_vol1,
                total_volume=total_volume,
                timestamp=ts
            )

            if self.queue:
                await self.queue.put(snapshot)
