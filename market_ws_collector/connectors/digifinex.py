import asyncio
import json
import time
import zlib
import websockets

from config import DEFAULT_SYMBOLS, WS_ENDPOINTS
from models.base import MarketSnapshot, SubscriptionRequest
from connectors.base import BaseAsyncConnector

class Connector(BaseAsyncConnector):
    def __init__(self, exchange="digifinex", symbols=None, ws_url=None, queue=None):
        super().__init__(exchange)
        self.queue = queue
        self.ws_url = ws_url or WS_ENDPOINTS.get(exchange)

        self.raw_symbols = symbols or DEFAULT_SYMBOLS.get(exchange, [])
        self.formatted_symbols = [self.format_symbol(sym) for sym in self.raw_symbols]

        self.subscriptions = [
            SubscriptionRequest(symbol=sym, channel="ticker")
            for sym in self.formatted_symbols
        ]

        # 映射：BTCUSDTPERP → BTC-USDT
        self.symbol_map = {
            self.format_symbol(raw): raw
            for raw in self.raw_symbols
        }

        self.ws = None

    def format_symbol(self, generic_symbol: str) -> str:
        return generic_symbol.upper().replace("-", "").replace("_", "") + "PERP"

    def decompress(self, payload: bytes) -> str:
        try:
            text = zlib.decompress(payload).decode("utf-8")
            return text
        except:
            return ""

    def build_sub_msg(self):
        return {
            "event": "ticker.subscribe",
            "id": 1,
            "instrument_ids": self.formatted_symbols
        }

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url)
        print(f"✅ Digifinex WebSocket 已连接 → {self.ws_url}")

    async def subscribe(self):
        msg = self.build_sub_msg()
        await self.ws.send(json.dumps(msg))
        await self.ws.send(json.dumps({"id": 99, "event": "server.ping"}))
        print(f"📨 已发送订阅: {msg}")
        await asyncio.sleep(0.2)

    async def run(self):
        while True:
            try:
                await self.connect()
                await self.subscribe()

                while True:
                    raw = await self.ws.recv()
                    if isinstance(raw, bytes):
                        raw = self.decompress(raw)

                    try:
                        data = json.loads(raw)
                    except:
                        continue

                    if "result" in data and isinstance(data["result"].get("data"), list):
                        for item in data["result"]["data"]:
                            symbol = item.get("i", "")
                            raw_symbol = self.symbol_map.get(symbol, symbol)

                            bid1 = float(item.get("b", 0.0))
                            ask1 = float(item.get("k", 0.0))
                            bid_vol1 = float(item.get("bs", 0.0))
                            ask_vol1 = float(item.get("ks", 0.0))
                            total_volume = float(item.get("vv", item.get("v", 0.0)))
                            ts = int(item.get("t", time.time() * 1000))

                            snapshot = MarketSnapshot(
                                exchange=self.exchange_name,
                                symbol=symbol,
                                raw_symbol=raw_symbol,
                                bid1=bid1,
                                ask1=ask1,
                                bid_vol1=bid_vol1,
                                ask_vol1=ask_vol1,
                                total_volume=total_volume,
                                timestamp=ts
                            )

                            if self.queue:
                                await self.queue.put(snapshot)
                                print(f"📥 {self.format_snapshot(snapshot)}")

            except Exception as e:
                print(f"❌ Digifinex 异常: {e}")
                await asyncio.sleep(0.5)
