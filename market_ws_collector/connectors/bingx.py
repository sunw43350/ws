import asyncio
import json
import time
import websockets
import gzip

from config import DEFAULT_SYMBOLS, WS_ENDPOINTS
from models.base import SubscriptionRequest, MarketSnapshot
from connectors.base import BaseAsyncConnector

class Connector(BaseAsyncConnector):
    def __init__(self, exchange="bingx", symbols=None, ws_url=None, queue=None):
        super().__init__(exchange)
        self.queue = queue
        self.ws_url = ws_url or WS_ENDPOINTS.get(exchange)

        generic_symbols = symbols or DEFAULT_SYMBOLS.get(exchange, [])
        self.subscriptions = [
            SubscriptionRequest(symbol=self.format_symbol(sym), channel="depth")
            for sym in generic_symbols
        ]

        self.symbol_map = {
            self.format_symbol(sym): sym
            for sym in generic_symbols
        }

        self.ws = None

    def format_symbol(self, generic_symbol: str) -> str:
        return generic_symbol.upper()

    def build_sub_msg(self, request: SubscriptionRequest, index: int) -> dict:
        return {
            "id": f"depth-{index+1}",
            "reqType": "sub",
            "dataType": f"{request.symbol}@depth20"
        }

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url)
        print(f"✅ BingX WebSocket 已连接 → {self.ws_url}")

    async def subscribe(self):
        for i, req in enumerate(self.subscriptions):
            sub_msg = self.build_sub_msg(req, i)
            await self.ws.send(json.dumps(sub_msg))
            print(f"📨 已订阅: {sub_msg['dataType']}")
            await asyncio.sleep(0.1)

    async def run(self):
        while True:
            try:
                await self.connect()
                await self.subscribe()

                while True:
                    raw = await self.ws.recv()

                    decompressed = gzip.decompress(raw).decode("utf-8")
                    data = json.loads(decompressed)

                    # print(data)


                    if "data" in data and "bids" in data["data"] and "asks" in data["data"]:
                        symbol_full = data.get("dataType", "").split("@")[0]
                        raw_symbol = self.symbol_map.get(symbol_full, symbol_full)

                        bids = data["data"].get("bids", [])
                        asks = data["data"].get("asks", [])

                        bid1, bid_vol1 = map(float, bids[0]) if bids else (0.0, 0.0)
                        ask1, ask_vol1 = map(float, asks[-1]) if asks else (0.0, 0.0)

                        ts = data["data"].get("ts") or data.get("ts") or int(time.time() * 1000)

                        snapshot = MarketSnapshot(
                            exchange=self.exchange_name,
                            symbol=symbol_full,
                            raw_symbol=raw_symbol,
                            bid1=bid1,
                            ask1=ask1,
                            bid_vol1=bid_vol1,
                            ask_vol1=ask_vol1,
                            timestamp=int(ts)
                        )

                        if self.queue:
                            await self.queue.put(snapshot)

            except websockets.exceptions.ConnectionClosedOK as e:
                self.log(f"🔁 BingX 正常断开: {e}，尝试重连...")
                await asyncio.sleep(0.1)
            except Exception as e:
                self.log(f"❌ BingX 异常: {e}")
                await asyncio.sleep(0.1)
