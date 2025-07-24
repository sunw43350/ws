import asyncio
import json
import time
import websockets
import re

from config import DEFAULT_SYMBOLS, WS_ENDPOINTS
from models.base import SubscriptionRequest, MarketSnapshot
from connectors.base import BaseAsyncConnector


class Connector(BaseAsyncConnector):
    def __init__(self, exchange="bitmex", symbols=None, ws_url=None, queue=None):
        super().__init__(exchange)
        self.queue = queue
        self.ws_url = ws_url or WS_ENDPOINTS.get(exchange)
        self.symbols = symbols or DEFAULT_SYMBOLS.get(exchange, [])

        self.subscriptions = [
            SubscriptionRequest(symbol=self.format_symbol(sym), channel="quote")
            for sym in self.symbols
        ]

        self.symbol_map = {
            self.format_symbol(sym): sym
            for sym in self.symbols
        }

    def format_symbol(self, generic_symbol: str) -> str:
        symbol = generic_symbol.replace("-", "").upper()
        symbol = re.sub(r"USDT$", "USD", symbol)
        return symbol

    def build_sub_msg(self) -> dict:
        args = [f"quote:{req.symbol}" for req in self.subscriptions]
        return {
            "op": "subscribe",
            "args": args
        }

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url)
        self.log(f"✅ BitMEX WebSocket 已连接 → {self.ws_url}")

    async def subscribe(self):
        msg = self.build_sub_msg()
        await self.ws.send(json.dumps(msg))
        self.log(f"📨 已发送订阅请求: {msg}")

    async def handle_message(self, data):
        if data.get("table") == "quote" and "data" in data:
            for item in data["data"]:
                symbol = item.get("symbol")
                raw_symbol = self.symbol_map.get(symbol, symbol)

                try:
                    bid1 = float(item.get("bidPrice", 0.0))
                    bid_vol1 = float(item.get("bidSize", 0.0))
                    ask1 = float(item.get("askPrice", 0.0))
                    ask_vol1 = float(item.get("askSize", 0.0))
                except Exception as e:
                    self.log(f"⚠️ 数据解析失败: {e}", level="WARNING")
                    continue

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
        else:
            self.log(f"未知消息格式: {data}", level="WARNING")

    async def run(self):
        await self.run_forever()
