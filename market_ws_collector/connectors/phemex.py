import asyncio
import json
import time
import websockets

from config import DEFAULT_SYMBOLS, WS_ENDPOINTS
from models.base import SubscriptionRequest, MarketSnapshot
from connectors.base import BaseAsyncConnector


class Connector(BaseAsyncConnector):
    def __init__(self, exchange="phemex", symbols=None, ws_url=None, queue=None):
        super().__init__(exchange, ping_interval=30, ping_payload=None)
        self.queue = queue
        self.ws_url = ws_url or WS_ENDPOINTS.get(exchange)

        self.raw_symbols = symbols or DEFAULT_SYMBOLS.get(exchange, [])
        self.formatted_symbols = [self.format_symbol(sym) for sym in self.raw_symbols]

        self.subscriptions = [
            SubscriptionRequest(symbol=sym, channel="orderbook.subscribe")
            for sym in self.formatted_symbols
        ]

        self.symbol_map = {
            self.format_symbol(sym): sym
            for sym in self.raw_symbols
        }

    def format_symbol(self, symbol: str) -> str:
        # BTC-USDT → BTCUSD
        base, _ = symbol.upper().split("-")
        return f"{base}USD"

    def build_sub_msg(self, symbol: str, idx: int) -> dict:
        return {
            "id": idx,
            "method": "orderbook.subscribe",
            "params": [symbol]
        }

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url)
        self.log(f"✅ Phemex WebSocket 已连接 → {self.ws_url}")

    async def subscribe(self):
        for i, req in enumerate(self.subscriptions):
            msg = self.build_sub_msg(req.symbol, i + 1)
            await self.ws.send(json.dumps(msg))
            self.log(f"📨 已订阅: orderbook.subscribe → {req.symbol}")
            await asyncio.sleep(0.2)

    async def handle_message(self, data):
        # 忽略非行情推送
        if "symbol" not in data or "book" not in data:
            self.log(f"❗️ 未处理的消息: {data}", level="DEBUG")
            return

        symbol = data.get("symbol")
        raw_symbol = self.symbol_map.get(symbol, symbol)
        timestamp = int(data.get("timestamp", time.time_ns()) / 1e6)

        bids = data.get("book", {}).get("bids", [])
        asks = data.get("book", {}).get("asks", [])

        # self.log(f"📊 {self.exchange_name} {raw_symbol} 行情数据: {data}", level="DEBUG")

        bid1, bid_vol1 = (0.0, 0.0)
        ask1, ask_vol1 = (0.0, 0.0)

        if bids:
            bid1 = bids[0][0] 
            bid_vol1 = bids[0][1] 
        if asks:
            ask1 = asks[0][0]
            ask_vol1 = asks[0][1]

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
