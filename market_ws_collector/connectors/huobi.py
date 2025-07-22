import asyncio
import json
import time
import gzip
import websockets

from config import DEFAULT_SYMBOLS, WS_ENDPOINTS
from models.base import SubscriptionRequest, MarketSnapshot
from connectors.base import BaseAsyncConnector

class Connector(BaseAsyncConnector):
    def __init__(self, exchange="huobi", symbols=None, ws_url=None, queue=None):
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
        return generic_symbol.lower().replace("-", "")

    def build_sub_msg(self, symbol: str) -> dict:
        return {
            "sub": f"market.{symbol}.ticker",
            "id": symbol
        }

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url)
        print(f"✅ Huobi WebSocket 已连接 → {self.ws_url}")

    async def subscribe(self):
        for req in self.subscriptions:
            msg = self.build_sub_msg(req.symbol)
            await self.ws.send(json.dumps(msg))
            print(f"📨 已订阅: market.{req.symbol}.ticker")
            await asyncio.sleep(0.1)

    async def run(self):
        while True:
            try:
                await self.connect()
                await self.subscribe()

                while True:
                    raw = await self.ws.recv()

                    if isinstance(raw, bytes):
                        try:
                            raw = gzip.decompress(raw).decode("utf-8")
                        except:
                            continue

                    try:
                        data = json.loads(raw)
                    except:
                        continue

                    # ✅ 处理 ping/pong 心跳
                    if "ping" in data:
                        await self.ws.send(json.dumps({"pong": data["ping"]}))
                        continue

                    if "tick" in data and "ch" in data:
                        tick = data["tick"]
                        channel = data["ch"]  # e.g. market.btcusdt.ticker
                        symbol = channel.split(".")[1]
                        raw_symbol = self.symbol_map.get(symbol, symbol.upper())

                        bid1 = float(tick.get("bid", 0.0))
                        bid_vol1 = float(tick.get("bidSize", 0.0))
                        ask1 = float(tick.get("ask", 0.0))
                        ask_vol1 = float(tick.get("askSize", 0.0))
                        timestamp = int(tick.get("ts", time.time() * 1000))

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
                print(f"❌ Huobi 异常: {e}")
                await asyncio.sleep(0.5)
