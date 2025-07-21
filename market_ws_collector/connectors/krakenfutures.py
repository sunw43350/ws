import asyncio
import json
import re
import time
import websockets

from config import DEFAULT_SYMBOLS, WS_ENDPOINTS
from models.base import SubscriptionRequest, MarketSnapshot
from connectors.base import BaseAsyncConnector

class Connector(BaseAsyncConnector):
    def __init__(self, exchange="krakenfutures", symbols=None, ws_url=None, queue=None):
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
        # BTC-USDT → PI_XBTUSD
        symbol = generic_symbol.upper().replace("-", "")
        symbol = re.sub(r"USDT$", "USD", symbol)          # ✅ 替换结算币
        symbol = re.sub(r"^BTC", "XBT", symbol)           # ✅ 替换 BTC → XBT
        return f"PI_{symbol}"


    def build_sub_msg(self) -> dict:
        return {
            "event": "subscribe",
            "feeds": ["ticker"],
            "product_ids": [req.symbol for req in self.subscriptions]
        }

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url, ping_interval=30)
        print(f"✅ Kraken Futures WebSocket 已连接 → {self.ws_url}")

    async def subscribe(self):
        await self.ws.send(json.dumps(self.build_sub_msg()))
        print(f"📨 Kraken Futures 已订阅: {[req.symbol for req in self.subscriptions]}")

    async def handle_message(self, raw: str):
        try:
            data = json.loads(raw)

            print(f"📩 收到 Kraken Futures 消息: {data}")
            if data.get("feed") == "ticker" and "product_id" in data:
                symbol = data["product_id"]
                bid1 = float(data.get("bid", 0.0))
                ask1 = float(data.get("ask", 0.0))
                bid_vol1 = float(data.get("bid_size", 0.0))
                ask_vol1 = float(data.get("ask_size", 0.0))
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
        except Exception as e:
            print(f"❌ Kraken Futures 数据处理异常: {e}")

    async def run(self):
        while True:
            try:
                await self.connect()
                await self.subscribe()

                while True:
                    raw = await self.ws.recv()
                    await self.handle_message(raw)

            except websockets.exceptions.ConnectionClosedOK as e:
                print(f"🔁 Kraken Futures 正常断开: {e}，尝试重连...")
                await asyncio.sleep(0.1)
            except Exception as e:
                print(f"❌ Kraken Futures 异常: {e}")
                await asyncio.sleep(0.1)
