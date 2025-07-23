import asyncio
import json
import re
import time
import websockets

from config import DEFAULT_SYMBOLS, WS_ENDPOINTS
from models.base import SubscriptionRequest, MarketSnapshot
from connectors.base import BaseAsyncConnector

class Connector(BaseAsyncConnector):
    def __init__(self, exchange="ascendex", symbols=None, ws_url=None, queue=None):
        super().__init__(exchange)
        self.queue = queue
        self.ws_url = ws_url or WS_ENDPOINTS.get(exchange)

        generic_symbols = symbols or DEFAULT_SYMBOLS.get(exchange, [])
        self.subscriptions = [
            SubscriptionRequest(symbol=self.format_symbol(sym), channel="depth", depth_level=0)
            for sym in generic_symbols
        ]

        self.symbol_map = {
            self.format_symbol(sym): sym
            for sym in generic_symbols
        }

        self.ws = None

    def format_symbol(self, generic_symbol: str) -> str:
        return re.sub(r"-USDT$", "", generic_symbol.upper()) + "-PERP"

    def build_sub_msg(self, request: SubscriptionRequest) -> dict:
        return {
            "op": "sub",
            "id": f"{request.channel}_{request.symbol}",
            "ch": f"{request.channel}:{request.symbol}:{request.depth_level}"
        }

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url)
        print(f"✅ AscendEX WebSocket 已连接 → {self.ws_url}")

    async def subscribe(self):
        for req in self.subscriptions:
            await self.ws.send(json.dumps(self.build_sub_msg(req)))
            print(f"📨 已订阅: {req.symbol}")
            await asyncio.sleep(0.1)

    async def run(self):
        while True:
            try:
                await self.connect()
                await self.subscribe()

                while True:
                    raw = await self.ws.recv()
                    data = json.loads(raw)

                    if data.get("m") == "depth" and "symbol" in data:
                        symbol = data["symbol"]
                        raw_symbol = self.symbol_map.get(symbol, symbol)

                        bids = data["data"].get("bids", [])
                        asks = data["data"].get("asks", [])

                        bid1, bid_vol1 = map(float, bids[0]) if bids else (0.0, 0.0)
                        ask1, ask_vol1 = map(float, asks[0]) if asks else (0.0, 0.0)

                        # depth 数据无时间戳，使用本地时间
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
                self.log(f"🔁 AscendEX 正常断开: {e}，尝试重连...")

                await asyncio.sleep(0.1)
            except Exception as e:
                self.log(f"❌ AscendEX 异常: {e}")

                await asyncio.sleep(0.1)
