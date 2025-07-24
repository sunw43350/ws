import asyncio
import json
import time
import websockets



from config import DEFAULT_SYMBOLS, WS_ENDPOINTS
from models.base import SubscriptionRequest, MarketSnapshot
from connectors.base import BaseAsyncConnector


class Connector(BaseAsyncConnector):
    def __init__(self, exchange="bitget", symbols=None, ws_url=None, queue=None):
        super().__init__(
            exchange=exchange,
            compression="zlib",  # ✅ 启用 zlib 解压支持
            ping_interval=10,
            ping_payload="ping",
            pong_keywords=["pong"]
        )
        self.queue = queue
        self.ws_url = ws_url or WS_ENDPOINTS.get(exchange)

        generic_symbols = symbols or DEFAULT_SYMBOLS.get(exchange, [])
        self.subscriptions = [
            SubscriptionRequest(symbol=self.format_symbol(sym), channel="books5")
            for sym in generic_symbols
        ]

        self.symbol_map = {
            self.format_symbol(sym): sym
            for sym in generic_symbols
        }

    def format_symbol(self, generic_symbol: str) -> str:
        return generic_symbol.replace("-", "").upper()

    def build_sub_msg(self) -> dict:
        return {
            "op": "subscribe",
            "args": [
                {
                    "instType": "USDT-FUTURES",
                    "channel": "books5",
                    "instId": req.symbol
                } for req in self.subscriptions
            ]
        }

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url)
        self.log(f"✅ Bitget WebSocket 已连接 → {self.ws_url}")

    async def subscribe(self):
        msg = self.build_sub_msg()
        await self.ws.send(json.dumps(msg))
        self.log(f"📨 已发送订阅请求: {msg}")

    async def handle_message(self, data):
        if "data" in data and "arg" in data:
            symbol = data["arg"].get("instId", "unknown")
            raw_symbol = self.symbol_map.get(symbol, symbol)
            orderbook = data["data"][0]
            bids = orderbook.get("bids", [])
            asks = orderbook.get("asks", [])

            bid1, bid_vol1 = map(float, bids[0]) if bids else (0.0, 0.0)
            ask1, ask_vol1 = map(float, asks[0]) if asks else (0.0, 0.0)
            timestamp = int(time.time() * 1000)

            snapshot = MarketSnapshot(
                exchange=self.exchange_name,
                symbol=symbol,
                raw_symbol=raw_symbol,
                bid1=bid1,
                ask1=ask1,
                bid_vol1=bid_vol1,
                ask_vol1=ask_vol1,
                timestamp=timestamp
            )

            if self.queue:
                await self.queue.put(snapshot)

    async def run(self):
        await self.run_forever()
