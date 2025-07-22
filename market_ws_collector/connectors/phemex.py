import asyncio
import json
import time
import websockets

from config import DEFAULT_SYMBOLS, WS_ENDPOINTS
from models.base import SubscriptionRequest, MarketSnapshot
from connectors.base import BaseAsyncConnector

class Connector(BaseAsyncConnector):
    def __init__(self, exchange="phemex", symbols=None, ws_url=None, queue=None):
        super().__init__(exchange)
        self.queue = queue
        self.ws_url = ws_url or WS_ENDPOINTS.get(exchange)

        self.raw_symbols = symbols or DEFAULT_SYMBOLS.get(exchange, [])
        self.formatted_symbols = [self.format_symbol(s) for s in self.raw_symbols]

        self.subscriptions = [
            SubscriptionRequest(symbol=sym, channel="orderbook.subscribe")
            for sym in self.formatted_symbols
        ]

        self.symbol_map = {
            self.format_symbol(s): s
            for s in self.raw_symbols
        }

        self.ws = None

    def format_symbol(self, symbol: str) -> str:
        # BTC-USDT → BTCUSD
        return symbol.upper().replace("-", "")[:-4] + "USD"

    def build_sub_msg(self, symbol: str, idx: int) -> dict:
        return {
            "id": idx,
            "method": "orderbook.subscribe",
            "params": [symbol]
        }

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url)
        print(f"✅ Phemex WebSocket 已连接 → {self.ws_url}")

    async def subscribe(self):
        for i, req in enumerate(self.subscriptions):
            msg = self.build_sub_msg(req.symbol, i + 1)
            await self.ws.send(json.dumps(msg))
            print(f"📨 已订阅: orderbook.subscribe → {req.symbol}")
            await asyncio.sleep(0.2)

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

                    print(f"📥 收到数据: {data}")

                    if "type" in data and data["type"] == "snapshot" and "book" in data:
                        symbol = data.get("symbol")
                        raw_symbol = self.symbol_map.get(symbol, symbol)
                        tick = data["book"]

                        bids = tick.get("bids", [])
                        asks = tick.get("asks", [])

                        bid1, bid_vol1 = map(lambda x: x / 1e4, bids[0]) if bids else (0.0, 0.0)
                        ask1, ask_vol1 = map(lambda x: x / 1e4, asks[0]) if asks else (0.0, 0.0)
                        timestamp = int(data.get("timestamp", time.time_ns()) / 1e6)  # 转毫秒

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
                            # print(f"📥 {self.format_snapshot(snapshot)}")



            except Exception as e:
                print(f"❌ Phemex 异常: {e}")
                await asyncio.sleep(0.5)
