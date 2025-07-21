import asyncio
import json
import time
import re
import websockets

from config import DEFAULT_SYMBOLS, WS_ENDPOINTS
from models.base import SubscriptionRequest, MarketSnapshot
from connectors.base import BaseAsyncConnector

class Connector(BaseAsyncConnector):
    def __init__(self, exchange="kraken", symbols=None, ws_url=None, queue=None):
        super().__init__(exchange)
        self.queue = queue
        self.ws_url = ws_url or WS_ENDPOINTS.get(exchange)

        generic_symbols = symbols or DEFAULT_SYMBOLS.get(exchange, [])
        self.subscriptions = [
            SubscriptionRequest(symbol=self.format_symbol(sym), channel="ticker")
            for sym in generic_symbols
        ]
        self.ws = None

    def format_symbol(self, generic_symbol: str) -> str:
        # 标准化 BTC-USDT → BTC/USD
        return re.sub(r"-", "/", generic_symbol.upper())

    def build_sub_msg(self) -> dict:
        return {
            "method": "subscribe",
            "params": {
                "channel": "ticker",
                "symbol": [req.symbol for req in self.subscriptions]
            }
        }

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url)
        print(f"✅ Kraken Spot WebSocket 已连接 → {self.ws_url}")

    async def subscribe(self):
        msg = self.build_sub_msg()
        await self.ws.send(json.dumps(msg))
        print(f"📨 Kraken Spot 已订阅: {[req.symbol for req in self.subscriptions]}")

    async def run(self):
        while True:
            try:
                await self.connect()
                await self.subscribe()

                while True:
                    raw = await self.ws.recv()
                    data = json.loads(raw)

                    print("📩 收到消息:", data)

                    channel = data.get("channel")
                    if channel != "ticker":
                        continue
                    data = data['data'][0] 

                    if channel == "ticker" and "symbol" in data:
                        symbol = data["symbol"]
                        bid1 = float(data.get("bid", 0.0))
                        ask1 = float(data.get("ask", 0.0))
                        bid_vol1 = float(data.get("bid_qty", 0.0))
                        ask_vol1 = float(data.get("ask_qty", 0.0))
                        total_volume = float(data.get("volume", 0.0))

                        snapshot = MarketSnapshot(
                            exchange=self.exchange_name,
                            symbol=symbol,
                            bid1=bid1,
                            ask1=ask1,
                            bid_vol1=bid_vol1,
                            ask_vol1=ask_vol1,
                            total_volume=total_volume,
                            timestamp=time.time()
                        )

                        if self.queue:
                            await self.queue.put(snapshot)

            except websockets.exceptions.ConnectionClosedOK as e:
                print(f"🔁 Kraken Spot 正常断开: {e}，尝试重连...")
                await asyncio.sleep(0.1)
            except Exception as e:
                print(f"❌ Kraken Spot 异常: {e}")
                await asyncio.sleep(0.1)
