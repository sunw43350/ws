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
        self.exchange_name = "ascendex"
        self.ws_url = ws_url or WS_ENDPOINTS.get(self.exchange_name)
        self.queue = queue

        generic_symbols = symbols or DEFAULT_SYMBOLS.get(self.exchange_name, [])
        self.subscriptions = [
            SubscriptionRequest(symbol=self.format_symbol(sym), channel="depth", depth_level=0)
            for sym in generic_symbols
        ]
        self.ws = None

    def format_symbol(self, generic_symbol: str) -> str:
        # BTC-USDT → BTC-PERP
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

    async def subscribe(self, request: SubscriptionRequest):
        msg = self.build_sub_msg(request)
        await self.ws.send(json.dumps(msg))
        print(f"📨 已订阅: {request.symbol}")

    async def run(self):
        while True:
            try:
                await self.connect()
                for req in self.subscriptions:
                    await self.subscribe(req)
                    await asyncio.sleep(0.2)

                while True:
                    raw = await self.ws.recv()
                    data = json.loads(raw)

                    if data.get("m") == "depth" and "symbol" in data:
                        symbol = data["symbol"]
                        bids = data["data"].get("bids", [])
                        asks = data["data"].get("asks", [])

                        bid1, bid_vol1 = map(float, bids[0]) if bids else (0.0, 0.0)
                        ask1, ask_vol1 = map(float, asks[0]) if asks else (0.0, 0.0)

                        snapshot = MarketSnapshot(
                            exchange=self.exchange_name,
                            symbol=symbol,
                            bid1=bid1,
                            ask1=ask1,
                            bid_vol1=bid_vol1,
                            ask_vol1=ask_vol1,
                            timestamp=time.time()
                        )

                        if self.queue:
                            await self.queue.put(snapshot)

            except websockets.exceptions.ConnectionClosedOK as e:
                print(f"🔁 AscendEX 正常断开: {e}，尝试重连...")
                await asyncio.sleep(2)
            except Exception as e:
                print(f"❌ AscendEX 异常: {e}")
                await asyncio.sleep(2)
