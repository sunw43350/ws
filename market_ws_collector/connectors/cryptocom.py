import asyncio
import json
import time
import websockets

from config import DEFAULT_SYMBOLS, WS_ENDPOINTS
from models.base import SubscriptionRequest, MarketSnapshot
from connectors.base import BaseAsyncConnector

class Connector(BaseAsyncConnector):
    def __init__(self, exchange="cryptocom", symbols=None, ws_url=None, queue=None):
        super().__init__(exchange)
        self.queue = queue
        self.ws_url = ws_url or WS_ENDPOINTS.get(exchange)

        self.raw_symbols = symbols or DEFAULT_SYMBOLS.get(exchange, [])
        self.formatted_symbols = [self.format_symbol(sym) for sym in self.raw_symbols]

        self.subscriptions = [
            SubscriptionRequest(symbol=sym, channel="ticker")
            for sym in self.formatted_symbols
        ]

        self.symbol_map = {
            self.format_symbol(raw): raw
            for raw in self.raw_symbols
        }

        self.ws = None

    def format_symbol(self, generic_symbol: str) -> str:
        return generic_symbol.replace("-", "_").upper()

    def build_sub_msg(self, symbol: str, req_id: int) -> dict:
        return {
            "id": req_id,
            "method": "subscribe",
            "params": {
                "channels": [f"ticker.{symbol}"]
            }
        }

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url)
        print(f"✅ Crypto.com WebSocket 已连接 → {self.ws_url}")

    async def subscribe(self):
        for i, req in enumerate(self.subscriptions):
            msg = self.build_sub_msg(req.symbol, i + 1)
            await self.ws.send(json.dumps(msg))
            print(f"📨 已订阅 ticker.{req.symbol}")
            await asyncio.sleep(0.1)

    async def run(self):
        while True:
            try:
                await self.connect()
                await self.subscribe()

                while True:
                    raw = await self.ws.recv()
                    try:
                        data = json.loads(raw)
                    except:
                        continue

                    

                    if data.get("method") == "ticker.update" and "params" in data:
                        tick = data["params"]
                        channel = tick.get("channel", "")
                        symbol = channel.replace("ticker.", "")
                        raw_symbol = self.symbol_map.get(symbol, symbol)

                        b = tick.get("data", {}).get("b", "0")     # bid price
                        bs = tick.get("data", {}).get("bs", "0")  # bid size
                        k = tick.get("data", {}).get("k", "0")     # ask price
                        ks = tick.get("data", {}).get("ks", "0")  # ask size

                        bid1 = float(b)
                        bid_vol1 = float(bs)
                        ask1 = float(k)
                        ask_vol1 = float(ks)
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
                            print(f"📥 {self.format_snapshot(snapshot)}")

            except Exception as e:
                print(f"❌ Crypto.com 异常: {e}")
                await asyncio.sleep(0.5)
