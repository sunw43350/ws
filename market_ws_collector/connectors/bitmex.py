import asyncio
import json
import time
import websockets

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

        self.ws = None

    def format_symbol(self, generic_symbol: str) -> str:
        return generic_symbol.upper()  # BitMEX uses uppercase product IDs

    def build_sub_msg(self):
        args = [f"quote:{req.symbol}" for req in self.subscriptions]
        return {
            "op": "subscribe",
            "args": args
        }

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url)
        print(f"✅ BitMEX WebSocket 已连接 → {self.ws_url}")

    async def subscribe(self):
        msg = self.build_sub_msg()
        await self.ws.send(json.dumps(msg))
        print(f"📨 已发送订阅请求: {msg}")

    async def run(self):
        while True:
            try:
                await self.connect()
                await self.subscribe()

                while True:
                    raw = await self.ws.recv()
                    data = json.loads(raw)

                    # 🧊 忽略非行情信息
                    if data.get("info") or data.get("success"):
                        continue

                    # 📈 处理 quote 数据
                    if data.get("table") == "quote" and "data" in data:
                        for item in data["data"]:
                            symbol = item.get("symbol")
                            raw_symbol = self.symbol_map.get(symbol, symbol)

                            bid1 = float(item.get("bidPrice", 0.0))
                            bid_vol1 = float(item.get("bidSize", 0.0))
                            ask1 = float(item.get("askPrice", 0.0))
                            ask_vol1 = float(item.get("askSize", 0.0))
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
                                # 可选打印日志
                                # print(self.format_snapshot(snapshot))

            except websockets.exceptions.ConnectionClosedOK as e:
                print(f"🔁 BitMEX 正常断开: {e}，尝试重连...")
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"❌ BitMEX 异常: {e}")
                await asyncio.sleep(0.5)
