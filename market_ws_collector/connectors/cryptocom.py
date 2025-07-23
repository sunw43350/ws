import asyncio
import json
import time
import websockets

from config import DEFAULT_SYMBOLS, WS_ENDPOINTS
from models.base import SubscriptionRequest, MarketSnapshot
from connectors.base import BaseAsyncConnector

class Connector(BaseAsyncConnector):
    def __init__(self, exchange="cryptocom", symbols=None, ws_url=None, queue=None):
        super().__init__(exchange)
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
        return generic_symbol.replace("-", "_").upper()

    def build_sub_msg(self) -> list:
        # Crypto.com 每个订阅都得单独发送请求，这里准备消息列表
        msgs = []
        for i, req in enumerate(self.subscriptions, 1):
            msg = {
                "id": i,
                "method": "subscribe",
                "params": {
                    "channels": [f"ticker.{req.symbol}"]
                }
            }
            msgs.append(msg)
        return msgs

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url)
        self.log(f"✅ Crypto.com WebSocket 已连接 → {self.ws_url}")

    async def subscribe(self):
        # Crypto.com 订阅要逐条发送
        for msg in self.build_sub_msg():
            await self.ws.send(json.dumps(msg))
            self.log(f"📨 已发送订阅请求: {msg}")
            await asyncio.sleep(0.1)

    async def handle_message(self, data):
        # 处理订阅确认和行情消息
        if data.get("method") == "subscribe" and "result" in data:
            result = data["result"]
            raw_symbol = result.get("instrument_name")
            tick_data = result.get("data", [{}])[0]

            symbol = tick_data.get("i", raw_symbol)

            bid1 = float(tick_data.get("b", 0.0))
            bid_vol1 = float(tick_data.get("bs", 0.0))
            ask1 = float(tick_data.get("k", 0.0))
            ask_vol1 = float(tick_data.get("ks", 0.0))
            total_volume = float(tick_data.get("vv", tick_data.get("v", 0.0)))
            timestamp = int(tick_data.get("t", time.time() * 1000))

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
