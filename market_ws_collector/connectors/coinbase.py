import asyncio
import json
import time
import websockets
from datetime import datetime
from config import DEFAULT_SYMBOLS, WS_ENDPOINTS
from models.base import SubscriptionRequest, MarketSnapshot
from connectors.base import BaseAsyncConnector

class Connector(BaseAsyncConnector):
    def __init__(self, exchange="coinbase", symbols=None, ws_url=None, queue=None):
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
        return generic_symbol.upper()

    def build_sub_msg(self) -> dict:
        return {
            "type": "subscribe",
            "product_ids": [req.symbol for req in self.subscriptions],
            "channel": "ticker"
        }

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url)
        self.log(f"✅ Coinbase WebSocket 已连接 → {self.ws_url}")

    async def subscribe(self):
        msg = self.build_sub_msg()
        await self.ws.send(json.dumps(msg))
        self.log(f"📨 已发送订阅请求: {msg}")

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

                    if data.get("channel") == "ticker" and "events" in data:
                        for event in data["events"]:
                            if event.get("type") != "update":
                                continue

                            for ticker in event.get("tickers", []):
                                symbol = ticker.get("product_id")
                                raw_symbol = self.symbol_map.get(symbol, symbol)

                                bid1 = float(ticker.get("best_bid", 0.0))
                                ask1 = float(ticker.get("best_ask", 0.0))
                                bid_vol1 = float(ticker.get("best_bid_quantity", 0.0))
                                ask_vol1 = float(ticker.get("best_ask_quantity", 0.0))
                                total_volume = float(ticker.get("volume_24_h", 0.0))

                                ts_iso = data.get("timestamp")
                                if ts_iso:
                                    try:
                                        dt = datetime.fromisoformat(ts_iso.replace("Z", "+00:00"))
                                        ts = int(dt.timestamp() * 1000)
                                    except:
                                        ts = int(time.time() * 1000)
                                else:
                                    ts = int(time.time() * 1000)

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

            except Exception as e:
                self.log(f"❌ Coinbase 异常: {e}")
                await asyncio.sleep(0.5)
