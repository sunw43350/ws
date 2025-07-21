import asyncio
import json
import time
import websockets

from config import DEFAULT_SYMBOLS, WS_ENDPOINTS
from models.base import SubscriptionRequest, MarketSnapshot
from connectors.base import BaseAsyncConnector

class Connector(BaseAsyncConnector):
    def __init__(self, exchange="bitmart", symbols=None, ws_url=None, queue=None):
        super().__init__(exchange)
        self.queue = queue
        self.ws_url = ws_url or WS_ENDPOINTS.get(exchange)
        self.symbols = symbols or DEFAULT_SYMBOLS.get(exchange, [])

        self.subscriptions = [
            SubscriptionRequest(symbol=self.format_symbol(sym), channel="futures/ticker")
            for sym in self.symbols
        ]

        # 原始币对 → 格式化映射
        self.symbol_map = {
            self.format_symbol(sym): sym
            for sym in self.symbols
        }

        self.ws = None

    def format_symbol(self, generic_symbol: str) -> str:
        return generic_symbol.upper()

    def build_sub_msg(self) -> dict:
        return {
            "action": "subscribe",
            "args": [f"futures/ticker:{req.symbol}" for req in self.subscriptions]
        }

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url)
        print(f"✅ BitMart WebSocket 已连接 → {self.ws_url}")

    async def subscribe(self):
        sub_msg = self.build_sub_msg()
        await self.ws.send(json.dumps(sub_msg))
        print(f"📨 已发送订阅请求: {sub_msg}")

    async def run(self):
        while True:
            try:
                await self.connect()
                await self.subscribe()

                while True:
                    raw = await self.ws.recv()
                    data = json.loads(raw)

                    # print(data)
                    if isinstance(data, dict) and "data" in data and "symbol" in data["data"]:
                        item = data["data"]
                        symbol = item.get("symbol")
                        raw_symbol = self.symbol_map.get(symbol, symbol)

                        bid1 = float(item.get("bid_price", 0.0))
                        bid_vol1 = float(item.get("bid_vol", 0.0))
                        ask1 = float(item.get("ask_price", 0.0))
                        ask_vol1 = float(item.get("ask_vol", 0.0))
                        total_volume = float(item.get("volume_24", 0.0))
                        timestamp = int(time.time() * 1000)  # BitMart 无推送时间戳

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


            except websockets.exceptions.ConnectionClosedOK as e:
                print(f"🔁 BitMart 正常断开: {e}，尝试重连...")
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"❌ BitMart 异常: {e}")
                await asyncio.sleep(0.5)
