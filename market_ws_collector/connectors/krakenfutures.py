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

        # 标准格式 symbol 列表（如 BTC-USDT）
        generic_symbols = symbols or DEFAULT_SYMBOLS.get("kraken", [])

        # 构建 SubscriptionRequest 对象
        self.subscriptions = [
            SubscriptionRequest(symbol=self.format_symbol(sym), channel="ticker")
            for sym in generic_symbols
        ]

        self.ws = None

    def format_symbol(self, generic_symbol: str) -> str:
        """标准格式 BTC-USDT → Kraken 格式 BTC/USD"""
        return generic_symbol.replace("-", "/").upper()

    def build_sub_msg(self) -> dict:
        """Kraken 支持批量订阅，构建统一订阅消息"""
        return {
            "method": "subscribe",
            "params": {
                "channel": "ticker",
                "symbol": [req.symbol for req in self.subscriptions]
            }
        }

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url)
        print(f"✅ Kraken 已连接: {self.ws_url}")

    async def subscribe(self):
        msg = self.build_sub_msg()
        await self.ws.send(json.dumps(msg))
        print(f"📨 Kraken 订阅 ticker 合约: {[req.symbol for req in self.subscriptions]}")

    async def run(self):
        await self.connect()
        await self.subscribe()

        while True:
            try:
                raw = await self.ws.recv()
                data = json.loads(raw)

                # ticker 推送结构为 { "channel": "ticker", "symbol": "BTC/USD", "price": {...} }
                if data.get("channel") == "ticker" and "symbol" in data:
                    symbol = data["symbol"]
                    price_data = data.get("price", {})
                    bid = float(price_data.get("bid", 0.0))
                    ask = float(price_data.get("ask", 0.0))

                    snapshot = MarketSnapshot(
                        exchange=self.exchange_name,
                        symbol=symbol,
                        best_bid=bid,
                        best_ask=ask,
                        timestamp=time.time()
                    )

                    if self.queue:
                        await self.queue.put(snapshot)

            except Exception as e:
                print(f"❌ Kraken 异常: {e}")
                await asyncio.sleep(1)
