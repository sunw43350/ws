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
        self.log(f"✅ Crypto.com WebSocket 已连接 → {self.ws_url}")

    async def subscribe(self):
        for i, req in enumerate(self.subscriptions):
            msg = self.build_sub_msg(req.symbol, i + 1)
            await self.ws.send(json.dumps(msg))
            self.log(f"📨 已订阅 ticker.{req.symbol}")
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

                    # self.log(f"📩 收到消息: {data} ")
                    if data.get("method") == "subscribe" and "result" in data:
                        result = data["result"]
                        raw_symbol = result.get("instrument_name")
                        symbol = result.get("data", [{}])[0].get("i", raw_symbol)
                        tick = result.get("data", [{}])[0]

                        bid1 = float(tick.get("b", 0.0))
                        bid_vol1 = float(tick.get("bs", 0.0))
                        ask1 = float(tick.get("k", 0.0))
                        ask_vol1 = float(tick.get("ks", 0.0))
                        total_volume = float(tick.get("vv", tick.get("v", 0.0)))
                        timestamp = int(tick.get("t", time.time() * 1000))

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

            except Exception as e:
                self.log(f"❌ Crypto.com 异常: {e}")
                await asyncio.sleep(0.5)
