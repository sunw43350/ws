# market_ws_collector/connectors/kraken.py

import asyncio
import json
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
        # 将标准符号转换为 Kraken Futures 合约格式
        # 例如 BTC-USDT → pi_xbtusd

        symbol = generic_symbol.upper().replace("-", "")

        # 特殊币种处理：BTC → XBT（Kraken 使用 XBT 表示 BTC）
        symbol = re.sub(r"^BTC", "XBT", symbol)

        return f"pi_{symbol.lower()}"


    def build_sub_msg(self) -> dict:
        return {
            "event": "subscribe",
            "feeds": ["ticker"],
            "symbols": [req.symbol for req in self.subscriptions]
        }

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url)
        print(f"✅ Kraken Futures WebSocket 已连接 → {self.ws_url}")

    async def subscribe(self):
        msg = self.build_sub_msg()
        await self.ws.send(json.dumps(msg))
        print(f"📨 已订阅: {[req.symbol for req in self.subscriptions]}")

    async def run(self):
        while True:
            try:
                await self.connect()
                await self.subscribe()

                while True:
                    raw = await self.ws.recv()
                    data = json.loads(raw)

                    if data.get("feed") == "ticker" and "symbol" in data:
                        symbol = data["symbol"]
                        bid1 = float(data.get("bid", 0.0))
                        ask1 = float(data.get("ask", 0.0))
                        bid_vol1 = float(data.get("bidSize", 0.0))
                        ask_vol1 = float(data.get("askSize", 0.0))
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
                print(f"🔁 Kraken Futures 正常断开: {e}，尝试重连...")
                await asyncio.sleep(0.1)
            except Exception as e:
                print(f"❌ Kraken Futures 异常: {e}")
                await asyncio.sleep(0.1)


import asyncio
import json
import re
import time
import websockets

from config import DEFAULT_SYMBOLS, WS_ENDPOINTS
from models.base import SubscriptionRequest, MarketSnapshot
from connectors.base import BaseAsyncConnector

class Connector(BaseAsyncConnector):
    def __init__(self, symbols=None, ws_url=None, queue=None):
        super().__init__()
        self.ws_url = ws_url or WS_ENDPOINTS.get("kraken")
        self.queue = queue

        generic_symbols = symbols or DEFAULT_SYMBOLS.get("kraken", [])
        self.subscriptions = [
            SubscriptionRequest(symbol=self.format_symbol(sym), channel="ticker")
            for sym in generic_symbols
        ]
        self.ws = None

    def format_symbol(self, generic_symbol: str) -> str:
        return generic_symbol.replace("-", "/").upper()

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
        print(f"✅ Kraken WebSocket connected: {self.ws_url}")

    async def subscribe(self):
        await self.ws.send(json.dumps(self.build_sub_msg()))
        print(f"📨 Kraken subscribed: {[req.symbol for req in self.subscriptions]}")

    async def run(self):
        await self.connect()
        await self.subscribe()

        while True:
            try:
                raw = await self.ws.recv()
                data = json.loads(raw)

                if data.get("channel") == "ticker" and "symbol" in data:
                    symbol = data["symbol"]
                    price_data = data.get("price", {})

                    bid1 = float(price_data.get("bid", 0.0))
                    ask1 = float(price_data.get("ask", 0.0))
                    bid_vol1 = float(price_data.get("bidSize", 0.0))
                    ask_vol1 = float(price_data.get("askSize", 0.0))
                    total_volume = float(price_data.get("volume", 0.0))

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
                print(f"❌ Kraken Error: {e}")
                await asyncio.sleep(1)
