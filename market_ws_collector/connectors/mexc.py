import asyncio
import json
import time
import websockets

from config import DEFAULT_SYMBOLS, WS_ENDPOINTS
from models.base import SubscriptionRequest, MarketSnapshot
from connectors.base import BaseAsyncConnector

class Connector(BaseAsyncConnector):
    def __init__(self, exchange="mexc", symbols=None, ws_url=None, queue=None):
        super().__init__(exchange)
        self.queue = queue
        self.ws_url = ws_url or WS_ENDPOINTS.get(exchange)

        self.raw_symbols = symbols or DEFAULT_SYMBOLS.get(exchange, [])
        self.formatted_symbols = [self.format_symbol(sym) for sym in self.raw_symbols]

        self.subscriptions = [
            SubscriptionRequest(symbol=sym, channel="sub.ticker")
            for sym in self.formatted_symbols
        ]

        self.symbol_map = {
            self.format_symbol(raw): raw
            for raw in self.raw_symbols
        }

        self.ws = None

    def format_symbol(self, generic_symbol: str) -> str:
        return generic_symbol.replace("-", "_").upper()

    def build_sub_msg(self, symbol: str) -> dict:
        return {
            "method": "sub.ticker",
            "param": {
                "symbol": symbol
            }
        }

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url)
        print(f"✅ MEXC WebSocket 已连接 → {self.ws_url}")

    async def subscribe(self):
        for req in self.subscriptions:
            msg = self.build_sub_msg(req.symbol)
            await self.ws.send(json.dumps(msg))
            print(f"📨 已订阅: sub.ticker → {req.symbol}")
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

                    if data.get("method") == "ticker.update" and "param" in data:
                        tick = data["param"]
                        symbol = tick.get("symbol")
                        raw_symbol = self.symbol_map.get(symbol, symbol)

                        bid1 = float(tick.get("bid1", 0.0))
                        ask1 = float(tick.get("ask1", 0.0))
                        bid_vol1 = float(tick.get("bidSize", 0.0))
                        ask_vol1 = float(tick.get("askSize", 0.0))
                        total_volume = float(tick.get("volume", 0.0))
                        timestamp = int(tick.get("ts", time.time() * 1000))

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
                            print(f"📥 {self.format_snapshot(snapshot)}")

            except Exception as e:
                print(f"❌ MEXC 异常: {e}")
                await asyncio.sleep(0.5)
