import asyncio
import json
import time
import websockets

from config import DEFAULT_SYMBOLS, WS_ENDPOINTS
from models.base import SubscriptionRequest, MarketSnapshot
from connectors.base import BaseAsyncConnector


class Connector(BaseAsyncConnector):
    def __init__(self, exchange="gateio", symbols=None, ws_url=None, queue=None):
        super().__init__(
            exchange=exchange,
            compression=None,
            pong_keywords=["pong"],           # 检测到 pong 日志打印即可
            max_retries=10
        )
        self.queue = queue
        self.ws_url = ws_url or WS_ENDPOINTS.get(exchange)

        self.raw_symbols = symbols or DEFAULT_SYMBOLS.get(exchange, [])
        self.formatted_symbols = [self.format_symbol(sym) for sym in self.raw_symbols]

        self.subscriptions = [
            SubscriptionRequest(symbol=sym, channel="futures.book_ticker")
            for sym in self.formatted_symbols
        ]

        self.symbol_map = {
            self.format_symbol(raw): raw
            for raw in self.raw_symbols
        }

    def format_symbol(self, generic_symbol: str) -> str:
        return generic_symbol.replace("-", "_").upper()

    def build_sub_msg(self, symbol: str) -> dict:
        return {
            "time": int(time.time()),
            "channel": "futures.book_ticker",
            "event": "subscribe",
            "payload": [symbol]
        }

    async def keep_alive(self):
        self.log("🔄 启动 Gate.io 心跳任务")
        while True:
            ping_msg = {
                "time": int(time.time()),
                "channel": "futures.ping"
            }
            await self.ws.send(json.dumps(ping_msg))
            self.log(f"Sent Gate.io ping: {ping_msg}")
            await asyncio.sleep(10)

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url)
        self.log(f"✅ Gate.io WebSocket 已连接 → {self.ws_url}")

    async def subscribe(self):
        for req in self.subscriptions:
            msg = self.build_sub_msg(req.symbol)
            await self.ws.send(json.dumps(msg))
            self.log(f"📨 已订阅: futures.book_ticker → {req.symbol}")
            await asyncio.sleep(0.1)

    async def handle_message(self, data):
        if data.get("channel") == "futures.book_ticker" and data.get("event") == "update":
            tick = data.get("result", {})
            symbol = tick.get("s")
            raw_symbol = self.symbol_map.get(symbol, symbol)

            bid1 = float(tick.get("b", 0.0))
            bid_vol1 = float(tick.get("B", 0.0))
            ask1 = float(tick.get("a", 0.0))
            ask_vol1 = float(tick.get("A", 0.0))
            timestamp = int(tick.get("t", time.time() * 1000))

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
        else:
            self.log(f"❗️ 未处理的消息: {data}", level="DEBUG")