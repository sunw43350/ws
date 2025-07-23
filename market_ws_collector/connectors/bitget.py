import asyncio
import json
import time
import zlib
import websockets

from config import DEFAULT_SYMBOLS, WS_ENDPOINTS
from models.base import SubscriptionRequest, MarketSnapshot
from connectors.base import BaseAsyncConnector

class Connector(BaseAsyncConnector):
    def __init__(self, exchange="bitget", symbols=None, ws_url=None, queue=None):
        super().__init__(exchange)
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

        self.ws = None

    def format_symbol(self, generic_symbol: str) -> str:
        return generic_symbol.upper()

    

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
        self.log("📨 已发送订阅请求:", msg)

    async def run(self):
        while True:
            try:
                await self.connect()
                await self.subscribe()

                while True:
                    raw = await self.ws.recv()

                    # Bitget 使用 zlib 压缩
                    if isinstance(raw, bytes):
                        try:
                            raw = self.inflate(raw).decode("utf-8")
                        except:
                            continue

                    data = json.loads(raw)

                    if "data" in data and "arg" in data:
                        symbol = data["arg"].get("instId", "unknown")
                        raw_symbol = self.symbol_map.get(symbol, symbol)
                        bids = data["data"][0].get("bids", [])
                        asks = data["data"][0].get("asks", [])

                        # bid1, bid_vol1 = map(float, bids[0]) if bids else (0.0, 0.0)
                        # ask1, ask_vol1 = map(float, asks[0]) if asks else (0.0, 0.0)
                        bid1, bid_vol1, ask1, ask_vol1 = self.extract_top_bid_ask(bids, asks)

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

            except websockets.exceptions.ConnectionClosedOK as e:
                self.log(f"🔁 Bitget 正常断开: {e}，尝试重连...")
                await asyncio.sleep(0.5)
            except Exception as e:
                self.log(f"❌ Bitget 异常: {e}")
                await asyncio.sleep(0.5)
